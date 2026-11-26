from contextlib import contextmanager, redirect_stdout
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import io
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import threading
import unittest
from unittest import mock
import sys
import urllib.error
import uuid

import rt_packs
import release_here


@contextmanager
def serving(directory, requests=None):
    class QuietHandler(SimpleHTTPRequestHandler):
        def do_GET(self):
            if requests is not None:
                requests.append(self.path)
            super().do_GET()

        def log_message(self, format, *args):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", 0), partial(QuietHandler, directory=str(directory)))
    thread = threading.Thread(target=server.serve_forever)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


class PackTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1] / (".rt-pack-test-" + uuid.uuid4().hex)
        self.profile = self.root / "profile"
        self.project = self.profile / "project"
        self.assets = self.project / "resource" / "native_test"
        self.assets.mkdir(parents=True)
        (self.profile / rt_packs.MARKER).touch()
        (self.project / "sakana.proj").write_text("{}")
        (self.assets / "a.mdl").write_bytes(b"geometry" * 1000)
        (self.assets / "b.png").write_bytes(bytes(range(256)) * 4)
        self.output = self.root / "out"

    def tearDown(self):
        shutil.rmtree(self.root)

    def test_build_install_and_loose_override(self):
        source = rt_packs.build(self.project, self.output, limit=300)
        index = json.loads((source / "active.json").read_bytes())
        self.assertEqual(len(index["packs"]), 2)
        (self.assets / "b.png").write_bytes(b"local edit")
        self.assertEqual(rt_packs.install(self.profile, source, prune=True, _allow_fixture=True), 1)
        self.assertFalse((self.assets / "a.mdl").exists())
        self.assertEqual((self.assets / "b.png").read_bytes(), b"local edit")
        active = self.project / "rtpacks" / "active.json"
        self.assertEqual(json.loads(active.read_bytes()), index)
        self.assertEqual(rt_packs.install(self.profile, source, prune=True, _allow_fixture=True), 0)

    def test_corrupt_update_does_not_activate_or_remove_assets(self):
        source = rt_packs.build(self.project, self.output)
        index = json.loads((source / "active.json").read_bytes())
        pack = source / next(iter(index["packs"]))
        pack.write_bytes(pack.read_bytes()[:-1])
        with self.assertRaises(ValueError):
            rt_packs.install(self.profile, source, prune=True, _allow_fixture=True)
        self.assertFalse((self.project / "rtpacks" / "active.json").exists())
        self.assertTrue((self.assets / "a.mdl").exists())

    def test_update_keeps_old_generation_and_removes_only_known_old_data(self):
        first = rt_packs.build(self.project, self.output)
        rt_packs.install(self.profile, first, _allow_fixture=True)
        (self.assets / "a.mdl").write_bytes(b"new mesh" * 1000)
        second = rt_packs.build(self.project, self.output)
        (self.assets / "a.mdl").write_bytes(b"geometry" * 1000)
        (self.assets / "b.png").write_bytes(b"custom texture")
        self.assertEqual(rt_packs.install(self.profile, second, prune=True, _allow_fixture=True), 1)
        self.assertFalse((self.assets / "a.mdl").exists())
        self.assertEqual((self.assets / "b.png").read_bytes(), b"custom texture")
        root = self.project / "rtpacks"
        self.assertTrue((root / first.name).is_dir())
        self.assertEqual(json.loads((root / "active.json").read_bytes())["generation"], second.name)
        (self.assets / "a.mdl").write_bytes(b"third mesh")
        third = rt_packs.build(self.project, self.output)
        next(third.glob("*.pak")).write_bytes(b"damaged")
        with self.assertRaises(ValueError):
            rt_packs.install(self.profile, third, _allow_fixture=True)
        self.assertEqual(json.loads((root / "active.json").read_bytes())["generation"], second.name)

    def test_removed_pack_asset_only_prunes_unchanged_old_loose_copy(self):
        first = rt_packs.build(self.project, self.output)
        rt_packs.install(self.profile, first, _allow_fixture=True)
        replacement = self.root / "replacement" / "resource" / "native_test"
        replacement.mkdir(parents=True)
        (replacement / "b.png").write_bytes((self.assets / "b.png").read_bytes())
        second = rt_packs.build(self.root / "replacement", self.output, previous=first)
        (self.assets / "b.png").write_bytes(b"custom texture")
        self.assertEqual(rt_packs.install(self.profile, second, prune=True, _allow_fixture=True), 1)
        self.assertFalse((self.assets / "a.mdl").exists())
        self.assertEqual((self.assets / "b.png").read_bytes(), b"custom texture")

    def test_requires_isolated_profile(self):
        source = rt_packs.build(self.project, self.output)
        (self.profile / rt_packs.MARKER).unlink()
        with self.assertRaises(ValueError):
            rt_packs.install(self.profile, source, prune=True)

    def test_invalid_entry_and_oversized_asset_rejected(self):
        with self.assertRaises(ValueError):
            rt_packs.build(self.project, self.output, limit=10)
        source = rt_packs.build(self.project, self.output)
        index = json.loads((source / "active.json").read_bytes())
        index["entries"]["resource/native_test/../bad.mdl"] = next(iter(index["entries"].values()))
        with self.assertRaises(ValueError):
            rt_packs.verify(source, index)

    def test_incremental_reuses_unmodified_shards_and_handles_add_remove(self):
        first = rt_packs.build(self.project, self.output, limit=300)
        first_index = json.loads((first / "active.json").read_bytes())
        self.assertEqual(len(first_index["packs"]), 2)
        self.assertEqual(rt_packs.build(self.project, self.output, limit=300, previous=first), first)

        (self.assets / "a.mdl").write_bytes(b"edited geometry" * 1000)
        (self.assets / "c.mot").write_bytes(bytes(range(256)) * 4)
        second = rt_packs.build(self.project, self.output, limit=300, previous=first)
        second_index = json.loads((second / "active.json").read_bytes())
        self.assertEqual(first_index["packs"]["pack00001.pak"], second_index["packs"]["pack00001.pak"])
        self.assertGreater(len(second_index["packs"]), 2)

        (self.assets / "a.mdl").unlink()
        third = rt_packs.build(self.project, self.output, limit=300, previous=second)
        third_index = json.loads((third / "active.json").read_bytes())
        self.assertNotIn("resource/native_test/a.mdl", third_index["entries"])
        self.assertEqual(second_index["packs"]["pack00001.pak"], third_index["packs"]["pack00001.pak"])

    def test_sparse_overlay_add_change_and_explicit_remove(self):
        first = rt_packs.build(self.project, self.output, limit=300)
        overlay = self.root / "overlay" / "resource" / "native_test"
        overlay.mkdir(parents=True)
        (overlay / "c.mot").write_bytes(b"added animation")
        second = rt_packs.build(self.root / "overlay", self.output, limit=300, previous=first, overlay=True)
        index = json.loads((second / "active.json").read_bytes())
        self.assertEqual(set(index["entries"]), {
            "resource/native_test/a.mdl", "resource/native_test/b.png", "resource/native_test/c.mot"})
        (overlay / "a.mdl").write_bytes(b"replacement geometry")
        third = rt_packs.build(self.root / "overlay", self.output, limit=300, previous=second,
                               overlay=True, remove=["resource/native_test/b.png"])
        third_index = json.loads((third / "active.json").read_bytes())
        self.assertNotIn("resource/native_test/b.png", third_index["entries"])
        self.assertEqual(third_index["entries"]["resource/native_test/a.mdl"][3], len(b"replacement geometry"))
        with self.assertRaises(ValueError):
            rt_packs.build(self.root / "overlay", self.output, previous=third, overlay=True,
                           remove=["resource/native_test/a.mdl"])

    def test_extract_selected_asset_without_overwriting(self):
        source = rt_packs.build(self.project, self.output)
        overlay = self.root / "overlay"
        name = "resource/native_test/a.mdl"
        self.assertEqual(rt_packs.extract(source, overlay, [name]), 1)
        path = overlay / "resource" / "native_test" / "a.mdl"
        self.assertEqual(path.read_bytes(), (self.assets / "a.mdl").read_bytes())
        path.write_bytes(b"edited")
        with self.assertRaises(FileExistsError):
            rt_packs.extract(source, overlay, [name])
        self.assertEqual(path.read_bytes(), b"edited")
        with self.assertRaises(ValueError):
            rt_packs.extract(source, overlay, ["resource/native_test/../bad.mdl"])

    def test_installed_generation_supports_extract_and_sparse_build(self):
        source = rt_packs.build(self.project, self.output)
        rt_packs.install(self.profile, source, _allow_fixture=True)
        installed = self.project / "rtpacks" / source.name
        overlay = self.root / "overlay"
        name = "resource/native_test/a.mdl"
        self.assertEqual(rt_packs.extract(installed, overlay, [name]), 1)
        (overlay / name).write_bytes(b"edited geometry")
        updated = rt_packs.build(overlay, self.output, previous=installed, overlay=True)
        index = json.loads((updated / "active.json").read_bytes())
        self.assertEqual(index["entries"][name][3], len(b"edited geometry"))
        self.assertIn("resource/native_test/b.png", index["entries"])

        rt_packs.install(self.profile, updated, _allow_fixture=True)
        with self.assertRaisesRegex(ValueError, "does not match index"):
            rt_packs.extract(installed, self.root / "old-overlay", [name])

    def test_build_rejects_source_changes(self):
        compress = rt_packs.zlib.compress
        touched = False

        def mutate(data, level):
            nonlocal touched
            if not touched:
                touched = True
                (self.assets / "a.mdl").write_bytes(b"concurrent edit")
            return compress(data, level)

        with mock.patch.object(rt_packs.zlib, "compress", side_effect=mutate):
            with self.assertRaisesRegex(ValueError, "changed during build"):
                rt_packs.build(self.project, self.output)
        self.assertEqual(list(self.output.iterdir()), [])

    def test_stage_compatible_release_preserves_loose_manifest(self):
        source = rt_packs.build(self.project, self.output)
        index = json.loads((source / "active.json").read_bytes())
        repo = self.root / "release-source"
        repo.mkdir()
        game = "_tools/rpgcobo-tool/"
        source_game = Path(__file__).resolve().parents[1] / "_tools" / "rpgcobo-tool"
        required = ["boot.sk", "project/rt_pack.sk", "project/plugin/rokugan/RokuganUpdate.sk"]
        files = {}
        for name in required:
            data = (source_game / name).read_bytes()
            path = repo / game / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            files[game + name] = [rt_packs.signed_crc(data), len(data)]
        for name in rt_packs.CUTOVER_TOOLS:
            data = (Path(__file__).parent / name).read_bytes()
            path = repo / "tools" / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            files["tools/" + name] = [rt_packs.signed_crc(data), len(data)]
        for name, entry in index["entries"].items():
            files[game + "project/" + name] = [entry[4], entry[3]]
            target = repo / game / "project" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(self.project / name, target)
        old_pack = game + "project/rtpacks/v" + "0" * 24 + "/pack00000.pak"
        files[old_pack] = ["0", 1]
        manifest = repo / "rt_manifest.json"
        manifest.write_text(json.dumps({"version": 4, "files": files}))
        before = manifest.read_bytes()
        stage = self.root / "stage"
        rt_packs.stage_compatible_release(manifest, source, stage, 5)
        staged = json.loads((stage / "rt_manifest.json").read_bytes())
        self.assertEqual(staged["version"], 5)
        self.assertNotIn(old_pack, staged["files"])
        for name in index["entries"]:
            self.assertEqual(staged["files"][game + "project/" + name],
                             files[game + "project/" + name])
        target = stage / game / "project" / "rtpacks"
        self.assertEqual(json.loads((target / "active.json").read_bytes()), index)
        rt_packs.verify(target / source.name, index)
        self.assertEqual(manifest.read_bytes(), before)
        candidate_asset = repo / game / "project" / "resource/native_test/a.mdl"
        original = candidate_asset.read_bytes()
        candidate_asset.write_bytes(b"edited after staging")
        with self.assertRaisesRegex(ValueError, "Candidate asset differs"):
            rt_packs.apply_compatible_overlay(stage, repo)
        self.assertFalse((repo / game / "project/rtpacks/active.json").exists())
        candidate_asset.write_bytes(original)
        rt_packs.apply_compatible_overlay(stage, repo)
        self.assertEqual(candidate_asset.read_bytes(), original)
        self.assertEqual(json.loads(manifest.read_bytes()), staged)
        self.assertEqual(json.loads((repo / "version.json").read_bytes())["version"], 5)
        self.assertEqual((repo / game / "project/rtpacks/active.json").read_bytes(),
                         (target / "active.json").read_bytes())
        self.assertTrue((repo / game / "rtpack-tools" / "rt_pack_cutover.py").is_file())
        self.assertIn(game + "rtpack-tools/rt_pack_cutover.py", staged["files"])
        files[game + "project/resource/native_test/a.mdl"][0] = "0"
        manifest.write_text(json.dumps({"version": 4, "files": files}))
        with self.assertRaisesRegex(ValueError, "differs from pack"):
            rt_packs.stage_compatible_release(manifest, source, self.root / "bad-stage", 5)
        self.assertFalse((self.root / "bad-stage").exists())

        with self.assertRaisesRegex(ValueError, "Packed assets remain"):
            rt_packs.stage_compatible_release(manifest, source, self.root / "duplicate-stage", 5,
                                              pack_only=True)
        for name in index["entries"]:
            del files[game + "project/" + name]
        files[game + "project/resource/native_test/unpacked.mdl"] = ["0", 1]
        manifest.write_text(json.dumps({"version": 4, "files": files}))
        stage = self.root / "pack-only-stage"
        rt_packs.stage_compatible_release(manifest, source, stage, 5,
                                          staged_hashes={}, pack_only=True)
        staged = json.loads((stage / "rt_manifest.json").read_bytes())
        self.assertIn(game + "project/resource/native_test/unpacked.mdl", staged["files"])
        for name in index["entries"]:
            self.assertNotIn(game + "project/" + name, staged["files"])
        candidate_asset.write_bytes(b"local work in progress")
        rt_packs.apply_compatible_overlay(stage, repo, staged_hashes={}, pack_only=True)
        self.assertEqual(candidate_asset.read_bytes(), b"local work in progress")

    def test_release_script_stages_compatible_packs_without_deleting_loose(self):
        source = rt_packs.build(self.project, self.output)
        candidate = self.root / "candidate"
        game = candidate / "_tools" / "rpgcobo-tool"
        engine = Path(__file__).resolve().parents[1] / "_tools" / "rpgcobo-tool"
        paths = ["boot.sk", "project/rt_pack.sk", "project/plugin/rokugan/RokuganUpdate.sk"]
        for name in paths:
            target = game / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(engine / name, target)
        tool_paths = []
        for name in rt_packs.CUTOVER_TOOLS:
            target = candidate / "tools" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(Path(__file__).parent / name, target)
            tool_paths.append("tools/" + name)
        for path in self.assets.iterdir():
            target = game / "project" / "resource" / "native_test" / path.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
            paths.append("project/resource/native_test/" + path.name)
        (candidate / "version.json").write_text('{"version":4}', encoding="utf-8")
        git_files = "\n".join(["_tools/rpgcobo-tool/" + name for name in paths] + tool_paths)
        calls = []

        def fake_git(*args):
            calls.append(args)
            return git_files if args == ("ls-files",) else "test commit"

        cwd = os.getcwd()
        try:
            os.chdir(candidate)
            with mock.patch.object(sys, "argv", ["release_here.py", "test", "--pack-generation", str(source)]), \
                 mock.patch.object(release_here, "git", side_effect=fake_git), \
                 mock.patch.object(release_here.subprocess, "run", return_value=mock.Mock(returncode=0)), \
                 redirect_stdout(io.StringIO()):
                release_here.main()
        finally:
            os.chdir(cwd)
        manifest = json.loads((candidate / "rt_manifest.json").read_bytes())
        self.assertEqual(manifest["version"], 5)
        self.assertIn("_tools/rpgcobo-tool/project/resource/native_test/a.mdl", manifest["files"])
        self.assertTrue((game / "project" / "resource" / "native_test" / "a.mdl").is_file())
        self.assertTrue((game / "project" / "rtpacks" / "active.json").is_file())
        self.assertTrue((game / "rtpack-tools" / "rt_pack_cutover.py").is_file())
        self.assertTrue(any(args[0] == "commit" for args in calls))
        self.assertTrue(any(args[0] == "push" for args in calls))
        try:
            os.chdir(candidate)
            with mock.patch.object(sys, "argv", ["release_here.py", "test"]), \
                 mock.patch.object(release_here, "git") as git:
                with self.assertRaisesRegex(SystemExit, "supply a matching"):
                    release_here.main()
                git.assert_not_called()
        finally:
            os.chdir(cwd)
        scoped_files = dict(manifest["files"])
        scoped_files["other.txt"] = [rt_packs.signed_crc(b"approved"), len(b"approved")]
        (candidate / "other.txt").write_bytes(b"unrelated working edit")
        (candidate / "approved-paths.txt").write_text("tools/rt_packs.py\n", encoding="utf-8")
        calls.clear()
        try:
            os.chdir(candidate)
            version_bytes = Path("version.json").read_bytes()
            with mock.patch.object(sys, "argv", ["release_here.py", "test", "--scoped",
                                               "--paths-file", "approved-paths.txt",
                                               "--pack-generation", str(source)]), \
                 mock.patch.object(release_here, "git", side_effect=fake_git), \
                 mock.patch.object(release_here, "manifest_from_index", return_value=scoped_files), \
                 mock.patch.object(release_here.subprocess, "run",
                                   return_value=mock.Mock(returncode=0, stdout=version_bytes)), \
                 redirect_stdout(io.StringIO()):
                release_here.main()
        finally:
            os.chdir(cwd)
        new_manifest = json.loads((candidate / "rt_manifest.json").read_bytes())
        self.assertEqual(new_manifest["files"]["other.txt"], scoped_files["other.txt"])
        self.assertFalse(any(args == ("add", "-u") for args in calls))
        self.assertTrue(any(args[0] == "add" and args[1].startswith("--pathspec-from-file=") for args in calls))

    def test_index_release_ignores_unstaged_assets_and_uses_staged_tools(self):
        source = rt_packs.build(self.project, self.output)
        index = json.loads((source / "active.json").read_bytes())
        repo = self.root / "staged-candidate"
        repo.mkdir()
        game = "_tools/rpgcobo-tool/"
        engine = Path(__file__).resolve().parents[1] / "_tools" / "rpgcobo-tool"
        provider, files = {}, {}
        for name in ("boot.sk", "project/rt_pack.sk", "project/plugin/rokugan/RokuganUpdate.sk"):
            key = game + name
            provider[key] = (engine / name).read_bytes()
            files[key] = [rt_packs.signed_crc(provider[key]), len(provider[key])]
        for name in rt_packs.CUTOVER_TOOLS:
            key = "tools/" + name
            provider[key] = (Path(__file__).parent / name).read_bytes()
            files[key] = [rt_packs.signed_crc(provider[key]), len(provider[key])]
        hashes = {}
        for name, entry in index["entries"].items():
            path = repo / game / "project" / name
            path.parent.mkdir(parents=True, exist_ok=True)
            data = (self.project / name).read_bytes()
            path.write_bytes(data)
            hashes[name] = rt_packs.digest(data)
            files[game + "project/" + name] = [entry[4], entry[3]]
        changed = repo / game / "project/resource/native_test/a.mdl"
        changed.write_bytes(b"unstaged human-style edit")
        manifest = repo / "rt_manifest.json"
        manifest.write_text(json.dumps({"version": 4, "files": files}))
        stage = self.root / "index-stage"
        rt_packs.stage_compatible_release(manifest, source, stage, 5,
                                           staged_hashes=hashes, content_provider=provider.__getitem__)
        rt_packs.apply_compatible_overlay(stage, repo, staged_hashes=hashes)
        self.assertEqual(changed.read_bytes(), b"unstaged human-style edit")
        self.assertEqual((repo / game / "rtpack-tools/rt_packs.py").read_bytes(), provider["tools/rt_packs.py"])
        wrong = dict(hashes)
        wrong["resource/native_test/a.mdl"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "Staged asset differs"):
            rt_packs.stage_compatible_release(manifest, source, self.root / "bad-index-stage", 6,
                                               staged_hashes=wrong, content_provider=provider.__getitem__)

    def test_from_index_release_preserves_unstaged_shared_files(self):
        source = rt_packs.build(self.project, self.output)
        index = json.loads((source / "active.json").read_bytes())
        repo = self.root / "index-release"
        repo.mkdir()
        game = "_tools/rpgcobo-tool/"
        engine = Path(__file__).resolve().parents[1] / "_tools" / "rpgcobo-tool"
        blobs, files = {}, {}
        for name in ("boot.sk", "project/rt_pack.sk", "project/plugin/rokugan/RokuganUpdate.sk"):
            key = game + name
            blobs[key] = (engine / name).read_bytes()
        for name in (*rt_packs.CUTOVER_TOOLS, "release_here.py"):
            key = "tools/" + name
            blobs[key] = (Path(__file__).parent / name).read_bytes()
            path = repo / "tools" / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(blobs[key])
        blobs["version.json"] = b'{"version":4}'
        (repo / "version.json").write_bytes(blobs["version.json"])
        for name, data in blobs.items():
            if name != "version.json":
                files[name] = [rt_packs.signed_crc(data), len(data)]
        hashes = {}
        for name, entry in index["entries"].items():
            data = (self.project / name).read_bytes()
            target = repo / game / "project" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            hashes[name] = rt_packs.digest(data)
            files[game + "project/" + name] = [entry[4], entry[3]]
        human = repo / game / "project/resource/native_test/a.mdl"
        human.write_bytes(b"unstaged human WIP")
        shared = repo / "tools/gen_maps.py"
        shared.write_bytes(b"unstaged shared work")
        files["tools/gen_maps.py"] = [rt_packs.signed_crc(b"reviewed hunk"), len(b"reviewed hunk")]
        calls = []

        def fake_git(*args):
            calls.append(args)
            return "test commit"

        cwd = os.getcwd()
        try:
            os.chdir(repo)
            with mock.patch.object(sys, "argv", ["release_here.py", "test", "--from-index",
                                               "--pack-generation", str(source)]), \
                 mock.patch.object(release_here, "git", side_effect=fake_git), \
                 mock.patch.object(release_here, "indexed_bytes", side_effect=blobs.__getitem__), \
                 mock.patch.object(release_here, "release_index_signature", return_value="stable"), \
                 mock.patch.object(release_here, "manifest_from_index", return_value=(files, hashes)), \
                 mock.patch.object(release_here.subprocess, "run",
                                   return_value=mock.Mock(returncode=0, stdout=b"tools/gen_maps.py\0")), \
                 redirect_stdout(io.StringIO()):
                release_here.main()
        finally:
            os.chdir(cwd)
        self.assertEqual(human.read_bytes(), b"unstaged human WIP")
        self.assertEqual(shared.read_bytes(), b"unstaged shared work")
        released = json.loads((repo / "rt_manifest.json").read_bytes())
        self.assertEqual(released["files"]["tools/gen_maps.py"], files["tools/gen_maps.py"])
        self.assertFalse(any(args == ("add", "-u") for args in calls))
        self.assertTrue(any(args[0] == "commit" for args in calls))

    def test_from_index_rejects_reserved_paths_and_index_races(self):
        repo = self.root / "index-guards"
        (repo / "tools").mkdir(parents=True)
        blobs = {"version.json": b'{"version":4}'}
        (repo / "version.json").write_bytes(blobs["version.json"])
        for name in ("release_here.py", "rt_packs.py"):
            key = "tools/" + name
            blobs[key] = (Path(__file__).parent / name).read_bytes()
            (repo / key).write_bytes(blobs[key])
        calls = []
        cwd = os.getcwd()
        try:
            os.chdir(repo)
            with mock.patch.object(sys, "argv", ["release_here.py", "test", "--from-index",
                                               "--pack-generation", str(self.output)]), \
                 mock.patch.object(release_here, "git", side_effect=lambda *args: calls.append(args)), \
                 mock.patch.object(release_here, "indexed_bytes", side_effect=blobs.__getitem__), \
                 mock.patch.object(release_here.subprocess, "run",
                                   return_value=mock.Mock(returncode=0, stdout=b"version.json\0")), \
                 self.assertRaisesRegex(SystemExit, "Do not pre-stage"):
                release_here.main()
            with mock.patch.object(sys, "argv", ["release_here.py", "test", "--from-index",
                                               "--pack-generation", str(self.output)]), \
                 mock.patch.object(release_here, "git", side_effect=lambda *args: calls.append(args)), \
                 mock.patch.object(release_here.subprocess, "run",
                                   return_value=mock.Mock(returncode=0, stdout=b"tools/gen_maps.py\0")), \
                 mock.patch.object(release_here, "indexed_bytes", side_effect=blobs.__getitem__), \
                 mock.patch.object(release_here, "release_index_signature", side_effect=["before", "after"]), \
                 mock.patch.object(release_here, "manifest_from_index", return_value=({}, {})), \
                 mock.patch.object(rt_packs, "stage_compatible_release"), \
                 mock.patch.object(rt_packs, "apply_compatible_overlay") as apply, \
                 self.assertRaisesRegex(SystemExit, "index changed"):
                release_here.main()
            apply.assert_not_called()
        finally:
            os.chdir(cwd)
        self.assertFalse(any(args[0] in ("commit", "push") for args in calls))

    def test_scoped_release_manifest_uses_staged_bytes(self):
        candidate = self.root / "index-test"
        candidate.mkdir()
        subprocess.run(["git", "init", "-q", str(candidate)], check=True)
        path = candidate / "asset.bin"
        path.write_bytes(b"approved staged data")
        asset = candidate / "_tools" / "rpgcobo-tool" / "project" / "resource" / "native_human" / "a.png"
        asset.parent.mkdir(parents=True)
        asset.write_bytes(b"committed human asset")
        subprocess.run(["git", "-C", str(candidate), "add", "asset.bin",
                        "_tools/rpgcobo-tool/project/resource/native_human/a.png"], check=True)
        path.write_bytes(b"unrelated working edit")
        asset.write_bytes(b"unstaged human WIP")
        (candidate / "untracked.bin").write_bytes(b"untracked")
        cwd = os.getcwd()
        try:
            os.chdir(candidate)
            files, hashes = release_here.manifest_from_index(with_asset_hashes=True)
        finally:
            os.chdir(cwd)
            for entry in (candidate / ".git").rglob("*"):
                if entry.is_file():
                    entry.chmod(stat.S_IWRITE | stat.S_IREAD)
        self.assertEqual(files, {
            "asset.bin": [rt_packs.signed_crc(b"approved staged data"), len(b"approved staged data")],
            "_tools/rpgcobo-tool/project/resource/native_human/a.png":
                [rt_packs.signed_crc(b"committed human asset"), len(b"committed human asset")]
        })
        self.assertEqual(hashes, {"resource/native_human/a.png": rt_packs.digest(b"committed human asset")})

    def test_download_update_and_interrupted_download(self):
        first = rt_packs.build(self.project, self.output)
        with serving(self.output) as base:
            url = f"{base}/{first.name}/active.json"
            with self.assertRaises(ValueError):
                rt_packs.update_from_url(self.profile, url)
            self.assertEqual(rt_packs.update_from_url(self.profile, url, prune=True,
                                                      allow_http_loopback=True, _allow_fixture=True), 2)
            active = self.project / "rtpacks" / "active.json"
            old = active.read_bytes()
            (self.assets / "a.mdl").write_bytes(b"new model")
            second = rt_packs.build(self.project, self.output)
            index = json.loads((second / "active.json").read_bytes())
            pack = second / next(iter(index["packs"]))
            contents = pack.read_bytes()
            pack.write_bytes(contents[:-1])
            with self.assertRaises(ValueError):
                rt_packs.update_from_url(self.profile, f"{base}/{second.name}/active.json",
                                         allow_http_loopback=True, _allow_fixture=True)
            self.assertEqual(active.read_bytes(), old)
            self.assertEqual((self.assets / "a.mdl").read_bytes(), b"new model")
            pack.unlink()
            with self.assertRaises(urllib.error.HTTPError):
                rt_packs.update_from_url(self.profile, f"{base}/{second.name}/active.json",
                                         allow_http_loopback=True, _allow_fixture=True)
            self.assertEqual(active.read_bytes(), old)
            pack.write_bytes(contents)
            self.assertEqual(rt_packs.update_from_url(self.profile, f"{base}/{second.name}/active.json",
                                                      prune=True, allow_http_loopback=True, _allow_fixture=True), 1)
            self.assertEqual(json.loads(active.read_bytes())["generation"], second.name)
            self.assertFalse(any(self.profile.glob(".rt-pack-download-*")))

    def test_incremental_update_reuses_unchanged_downloads(self):
        first = rt_packs.build(self.project, self.output, limit=300)
        requests = []
        with serving(self.output, requests) as base:
            rt_packs.update_from_url(self.profile, f"{base}/{first.name}/active.json",
                                     allow_http_loopback=True, _allow_fixture=True)
            (self.assets / "a.mdl").write_bytes(b"edited geometry" * 1000)
            second = rt_packs.build(self.project, self.output, limit=300, previous=first)
            requests.clear()
            rt_packs.update_from_url(self.profile, f"{base}/{second.name}/active.json",
                                     allow_http_loopback=True, _allow_fixture=True)
            self.assertIn(f"/{second.name}/pack00000.pak", requests)
            self.assertNotIn(f"/{second.name}/pack00001.pak", requests)


if __name__ == "__main__":
    unittest.main()
