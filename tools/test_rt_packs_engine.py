"""Integration test against a private, minimal copy of the Windows runtime."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import unittest
from unittest import mock
import uuid

import rt_packs
from test_rt_packs import serving

if os.name == "nt":
    import rt_pack_cutover


ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "_tools" / "rpgcobo-tool"


@unittest.skipUnless(os.name == "nt" and (ENGINE / "rpgcobo.exe").is_file(), "Windows runtime required")
class EnginePackTests(unittest.TestCase):
    def setUp(self):
        self.root = ROOT / (".rt-pack-engine-test-" + uuid.uuid4().hex)
        self.root.mkdir()
        self.project = self.root / "project"
        self.project.mkdir()
        for name in ("rpgcobo.exe", "sakanagl.dll", "boot.sk"):
            shutil.copyfile(ENGINE / name, self.root / name)
        (self.root / "profile.json").write_text(json.dumps({
            "profile": str(self.root), "source": str(ENGINE),
        }), encoding="utf-8")
        shutil.copytree(ENGINE / "project" / "system", self.project / "system")
        shutil.copyfile(ENGINE / "project" / "rt_pack.sk", self.project / "rt_pack.sk")
        updater = self.project / "plugin" / "rokugan"
        updater.mkdir(parents=True)
        shutil.copyfile(ENGINE / "project" / "plugin" / "rokugan" / "RokuganUpdate.sk",
                        updater / "RokuganUpdate.sk")
        (self.project / "sakana.proj").write_text(
            '{"appname":"packtest","permission":{"file":[7],"addon":[1]}}', encoding="utf-8")
        self.assets = self.project / "resource" / "native_chara"
        (self.assets / "tex").mkdir(parents=True)
        for name in ("deduce_brush.mdl", "deduce_brush.pm", "tex/head_checks_color.png"):
            shutil.copyfile(ENGINE / "project" / "resource" / "native_chara" / name, self.assets / name)
        for name in ("os-temp", "roaming", "local"):
            (self.root / name).mkdir()
        rt_packs.enable_test_profile(self.root)

    def tearDown(self):
        shutil.rmtree(self.root)

    def run_engine(self, expected_crc, mounted=True):
        script = """
local model = getResource("/resource/native_chara/deduce_brush.mdl");
if (!model) throw "missing packed model";
local mesh = getPolygonMesh(getResource("/resource/native_chara/deduce_brush.pm"));
if (!mesh || !mesh.vtx) throw "invalid packed model";
local texture = getResource("/resource/native_chara/tex/head_checks_color.png");
if (!texture || !texture.getContent()) throw "invalid texture";
if (ByteBuffer() instanceof TempBuffer) throw "buffer types not distinguished";
if (!FileRef("project/resource/native_chara/tex/head_checks_color.png").exists()
    && !(texture.loadData() instanceof TempBuffer)) throw "packed resource must use a temporary buffer";
if (("" .. texture.loadData().crc32(0)) != "%s") throw "wrong texture precedence";
printf("[PACK TEST] model and texture OK\\n");
skExit(0);
""" % expected_crc
        (self.project / "testplay.sk").write_text(script, encoding="utf-8")
        env = os.environ.copy()
        env.update(TEMP=str(self.root / "os-temp"), TMP=str(self.root / "os-temp"),
                   APPDATA=str(self.root / "roaming"), LOCALAPPDATA=str(self.root / "local"))
        proc = subprocess.run([str(self.root / "rpgcobo.exe"), "-testplay"], cwd=self.root, env=env,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
        output = proc.stdout.decode("utf-8", errors="replace")
        if mounted:
            self.assertIn("[RT packs] Mounted 3 assets", output, output)
        else:
            self.assertNotIn("[RT packs] Mounted", output)
        self.assertIn("[PACK TEST] model and texture OK", output, output)
        self.assertNotIn("Exception in thread", output)

    def download_update(self, source, prune=False):
        with serving(self.root / "output") as base:
            return rt_packs.update_from_url(
                self.root, f"{base}/{source.name}/active.json",
                prune=prune, allow_http_loopback=True)

    def run_update_scan(self, expected, crc, size):
        script = """
::RPGStage <- { launch = function(opt=null) {} };
::Rokugan <- {};
runsk("/plugin/rokugan/RokuganUpdate.sk");
local path = "_tools/rpgcobo-tool/project/resource/native_chara/deduce_brush.mdl";
local files = {};
files[path] <- ["%s", %d];
local remote = { files = files };
local installedFiles = {};
installedFiles[path] <- [files[path][0], files[path][1]];
local installed = { files = installedFiles };
local need = ::Rokugan.updScan(remote, null, false);
if (length(need) != %d) throw "wrong verify result";
files[path][0] = "0";
if (length(::Rokugan.updScan(remote, installed, true)) != 1) throw "changed asset was skipped";
printf("[PACK TEST] updater scan OK\\n");
skExit(0);
""" % (crc, size, expected)
        (self.project / "testplay.sk").write_text(script, encoding="utf-8")
        env = os.environ.copy()
        env.update(TEMP=str(self.root / "os-temp"), TMP=str(self.root / "os-temp"),
                   APPDATA=str(self.root / "roaming"), LOCALAPPDATA=str(self.root / "local"))
        proc = subprocess.run([str(self.root / "rpgcobo.exe"), "-testplay"], cwd=self.root, env=env,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
        output = proc.stdout.decode("utf-8", errors="replace")
        self.assertIn("[PACK TEST] updater scan OK", output, output)
        self.assertNotIn("Exception in thread", output)

    def test_packed_model_texture_loose_override_and_bad_update(self):
        source = rt_packs.build(self.project, self.root / "output", limit=13000)
        index = json.loads((source / "active.json").read_bytes())
        self.assertEqual(len(index["packs"]), 2)
        texture = self.assets / "tex" / "head_checks_color.png"
        packed_crc = rt_packs.signed_crc(texture.read_bytes())
        self.assertEqual(self.download_update(source, prune=True), 3)
        self.run_engine(packed_crc)

        replacement = ENGINE / "project" / "resource" / "native_chara" / "tex" / "head_checks_normal.png"
        next_project = self.root / "next-project"
        next_assets = next_project / "resource" / "native_chara"
        (next_assets / "tex").mkdir(parents=True)
        for name in ("deduce_brush.mdl", "deduce_brush.pm"):
            shutil.copyfile(ENGINE / "project" / "resource" / "native_chara" / name, next_assets / name)
        shutil.copyfile(replacement, next_assets / "tex" / "head_checks_color.png")
        update = rt_packs.build(next_project, self.root / "output")
        self.assertEqual(self.download_update(update, prune=True), 0)
        updated_index = json.loads((update / "active.json").read_bytes())
        self.run_engine(rt_packs.signed_crc(replacement.read_bytes()))

        original = ENGINE / "project" / "resource" / "native_chara" / "tex" / "head_checks_color.png"
        texture.write_bytes(original.read_bytes())
        self.run_engine(rt_packs.signed_crc(texture.read_bytes()))

        shutil.copyfile(original, next_assets / "tex" / "head_checks_color.png")
        third = rt_packs.build(next_project, self.root / "output")
        third_index = json.loads((third / "active.json").read_bytes())
        for name in third_index["packs"]:
            (third / name).write_bytes(b"corrupt")
            break
        with self.assertRaises(ValueError):
            self.download_update(third, prune=True)
        self.assertEqual(json.loads((self.project / "rtpacks" / "active.json").read_bytes()), updated_index)
        self.run_engine(rt_packs.signed_crc(texture.read_bytes()))

    def test_incomplete_pack_set_falls_back_to_loose_files(self):
        source = rt_packs.build(self.project, self.root / "output")
        rt_packs.install(self.root, source)
        active = json.loads((self.project / "rtpacks" / "active.json").read_bytes())
        (self.project / "rtpacks" / active["generation"] / next(iter(active["packs"]))).unlink()
        texture = self.assets / "tex" / "head_checks_color.png"
        self.run_engine(rt_packs.signed_crc(texture.read_bytes()), mounted=False)

    def test_running_profile_cannot_be_updated(self):
        source = rt_packs.build(self.project, self.root / "output")
        (self.project / "testplay.sk").write_text(
            'local b = ByteBuffer(); b.putText("ready"); b.pos=0; '
            'FileRef("ready").save(b); sleep(30000); skExit(0);', encoding="utf-8")
        env = os.environ.copy()
        env.update(TEMP=str(self.root / "os-temp"), TMP=str(self.root / "os-temp"),
                   APPDATA=str(self.root / "roaming"), LOCALAPPDATA=str(self.root / "local"))
        proc = subprocess.Popen([str(self.root / "rpgcobo.exe"), "-testplay"], cwd=self.root, env=env,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            deadline = time.monotonic() + 15
            while not (self.root / "ready").exists() and proc.poll() is None and time.monotonic() < deadline:
                time.sleep(0.05)
            self.assertTrue((self.root / "ready").is_file(), "fixture engine did not start")
            self.assertIsNone(proc.poll())
            with self.assertRaises(RuntimeError):
                rt_packs.install(self.root, source, prune=True)
            with self.assertRaises(RuntimeError):
                rt_pack_cutover.prepare(self.root)
            self.assertFalse((self.project / "rtpacks" / "active.json").exists())
            self.assertTrue((self.assets / "deduce_brush.mdl").exists())
        finally:
            if proc.poll() is None:
                proc.terminate()
            proc.wait(timeout=10)

    def test_recoverable_cutover_preserves_edits_and_restores_from_pack(self):
        source = rt_packs.build(self.project, self.root / "output")
        rt_packs.install(self.root, source)
        name, count = rt_pack_cutover.prepare(self.root)
        self.assertEqual(count, 3)
        texture = self.assets / "tex" / "head_checks_color.png"
        edited = (ENGINE / "project" / "resource" / "native_chara" /
                  "tex" / "head_checks_normal.png").read_bytes()
        texture.write_bytes(edited)
        self.assertEqual(rt_pack_cutover.apply(self.root, name), 2)
        self.assertEqual(texture.read_bytes(), edited)
        self.run_engine(rt_packs.signed_crc(edited))
        self.assertEqual(rt_pack_cutover.seal(self.root, name), 2)
        restored, conflicts = rt_pack_cutover.restore(self.root, name)
        self.assertEqual(restored, 2)
        self.assertIn("resource/native_chara/tex/head_checks_color.png", conflicts)
        self.assertEqual(texture.read_bytes(), edited)
        self.assertEqual((self.assets / "deduce_brush.mdl").read_bytes(),
                         (ENGINE / "project" / "resource" / "native_chara" / "deduce_brush.mdl").read_bytes())

    def test_cutover_restores_quarantine_when_pack_is_corrupt(self):
        source = rt_packs.build(self.project, self.root / "output")
        rt_packs.install(self.root, source)
        name, count = rt_pack_cutover.prepare(self.root)
        self.assertEqual(rt_pack_cutover.apply(self.root, name), count)
        active = json.loads((self.project / "rtpacks" / "active.json").read_bytes())
        pack = self.project / "rtpacks" / active["generation"] / next(iter(active["packs"]))
        pack.write_bytes(b"corrupt")
        restored, conflicts = rt_pack_cutover.restore(self.root, name)
        self.assertEqual(restored, count)
        self.assertEqual(conflicts, [])
        self.assertTrue((self.assets / "deduce_brush.mdl").exists())

    def test_sealed_cutover_reports_missing_backup_when_pack_is_corrupt(self):
        source = rt_packs.build(self.project, self.root / "output")
        rt_packs.install(self.root, source)
        name, count = rt_pack_cutover.prepare(self.root)
        self.assertEqual(rt_pack_cutover.apply(self.root, name), count)
        self.assertEqual(rt_pack_cutover.seal(self.root, name), count)
        active = json.loads((self.project / "rtpacks" / "active.json").read_bytes())
        pack = self.project / "rtpacks" / active["generation"] / next(iter(active["packs"]))
        pack.write_bytes(b"corrupt")
        restored, conflicts = rt_pack_cutover.restore(self.root, name)
        self.assertEqual(restored, 0)
        self.assertEqual(len(conflicts), count)
        self.assertFalse((self.assets / "deduce_brush.mdl").exists())

    def test_cutover_exclusive_runtime_lock_blocks_launch(self):
        with rt_pack_cutover.stopped(self.root):
            with self.assertRaises(PermissionError):
                subprocess.Popen([str(self.root / "rpgcobo.exe"), "-testplay"], cwd=self.root)

    def test_bundled_cutover_tool_runs_without_repository_tools(self):
        source = rt_packs.build(self.project, self.root / "output")
        rt_packs.install(self.root, source)
        bundle = self.root / "rtpack-tools"
        bundle.mkdir()
        for name in rt_packs.CUTOVER_TOOLS:
            shutil.copyfile(ROOT / "tools" / name, bundle / name)
        (bundle / "loader.sha256").write_text(
            rt_packs.digest((self.project / "rt_pack.sk").read_bytes()), encoding="ascii")
        cli = [sys.executable, "-E", str(bundle / "rt_pack_cutover.py")]

        def run(*args):
            return subprocess.run(cli + list(args), cwd=self.root, capture_output=True, text=True, timeout=30)

        prepared = run("prepare", str(self.root))
        self.assertEqual(prepared.returncode, 0, prepared.stderr)
        ident = prepared.stdout.split()[1].rstrip(":")
        for op in ("apply", "seal"):
            result = run(op, str(self.root), ident)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "3")
        crc = rt_packs.signed_crc((ENGINE / "project" / "resource" / "native_chara" /
                                   "tex" / "head_checks_color.png").read_bytes())
        self.run_engine(crc)
        result = run("restore", str(self.root), ident)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.assets / "deduce_brush.mdl").is_file())
        (bundle / "loader.sha256").write_text("0" * 64, encoding="ascii")
        self.assertNotEqual(run("prepare", str(self.root)).returncode, 0)

    def test_interrupted_cutover_restores_already_moved_files(self):
        source = rt_packs.build(self.project, self.root / "output")
        rt_packs.install(self.root, source)
        name, _ = rt_pack_cutover.prepare(self.root)
        rename = os.rename
        count = 0

        def interrupted(src, dst):
            nonlocal count
            count += 1
            if count == 2:
                raise OSError("simulated interruption")
            return rename(src, dst)

        with mock.patch.object(rt_pack_cutover.os, "rename", side_effect=interrupted):
            with self.assertRaisesRegex(OSError, "simulated interruption"):
                rt_pack_cutover.apply(self.root, name)
        restored, _ = rt_pack_cutover.restore(self.root, name)
        self.assertEqual(restored, 1)
        self.assertTrue((self.assets / "deduce_brush.mdl").exists())

    def test_seal_keeps_changed_quarantine_and_restores_it(self):
        source = rt_packs.build(self.project, self.root / "output")
        rt_packs.install(self.root, source)
        name, count = rt_pack_cutover.prepare(self.root)
        self.assertEqual(rt_pack_cutover.apply(self.root, name), count)
        journal_root = self.root / ".rt-pack-transactions" / name
        journal = json.loads((journal_root / "journal.json").read_bytes())
        first = next(iter(journal["files"]))
        backup = journal_root.joinpath("loose", *first.split("/"))
        backup.write_bytes(b"concurrent edit")
        with self.assertRaisesRegex(ValueError, "changed"):
            rt_pack_cutover.seal(self.root, name)
        self.assertEqual(backup.read_bytes(), b"concurrent edit")
        rt_pack_cutover.restore(self.root, name)
        self.assertEqual(self.project.joinpath(*first.split("/")).read_bytes(), b"concurrent edit")

    def test_existing_updater_checks_pack_and_respects_loose_override(self):
        model = self.assets / "deduce_brush.mdl"
        raw = model.read_bytes()
        source = rt_packs.build(self.project, self.root / "output")
        index = json.loads((source / "active.json").read_bytes())
        self.download_update(source, prune=True)
        self.run_update_scan(0, rt_packs.signed_crc(raw), len(raw))
        entry = index["entries"]["resource/native_chara/deduce_brush.mdl"]
        pack = self.project / "rtpacks" / index["generation"] / entry[0]
        original = pack.read_bytes()
        damaged = bytearray(original)
        damaged[entry[1]] ^= 1
        pack.write_bytes(damaged)
        self.run_update_scan(1, rt_packs.signed_crc(raw), len(raw))
        pack.write_bytes(original)
        model.write_bytes(b"local edit")
        self.run_update_scan(1, rt_packs.signed_crc(raw), len(raw))

    def test_existing_updater_still_checks_unpacked_assets(self):
        raw = (self.assets / "deduce_brush.mdl").read_bytes()
        self.run_update_scan(0, rt_packs.signed_crc(raw), len(raw))

    def test_native_atomic_index_replace(self):
        script = """
local a = ByteBuffer(); a.putText("old"); a.pos=0;
local b = ByteBuffer(); b.putText("new"); b.pos=0;
FileRef("old-index").save(a); FileRef("new-index").save(b);
if (!FileRef("new-index").moveTo(FileRef("old-index"), 1)) throw "replace failed";
if (FileRef("old-index").load().asText() != "new") throw "wrong replacement";
printf("[PACK TEST] native replace OK\\n");
skExit(0);
"""
        (self.project / "testplay.sk").write_text(script, encoding="utf-8")
        env = os.environ.copy()
        env.update(TEMP=str(self.root / "os-temp"), TMP=str(self.root / "os-temp"),
                   APPDATA=str(self.root / "roaming"), LOCALAPPDATA=str(self.root / "local"))
        proc = subprocess.run([str(self.root / "rpgcobo.exe"), "-testplay"], cwd=self.root, env=env,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
        output = proc.stdout.decode("utf-8", errors="replace")
        self.assertIn("[PACK TEST] native replace OK", output, output)

    def test_updater_reuses_only_verified_installed_shards(self):
        source = rt_packs.build(self.project, self.root / "output")
        rt_packs.install(self.root, source)
        index = json.loads((source / "active.json").read_bytes())
        name = next(iter(index["packs"]))
        pack = self.project / "rtpacks" / source.name / name
        data = pack.read_bytes()
        script = """
::RPGStage <- { launch = function(opt=null) {} };
::Rokugan <- {};
runsk("/plugin/rokugan/RokuganUpdate.sk");
local p = "_tools/rpgcobo-tool/project/rtpacks/v000000000000000000000000/%s";
local good = ::Rokugan.updReusePack(p, ["%s", %d]);
if (!good || good.size != %d) throw "unchanged shard not reused";
local bad = ::Rokugan.updReusePack(p, ["0", %d]);
if (bad) throw "damaged shard reused";
if (::Rokugan.updReusePack("_tools/rpgcobo-tool/project/rtpacks/../%s", ["%s", %d]))
 throw "invalid generation accepted";
printf("[PACK TEST] shard reuse OK\\n");
skExit(0);
""" % (name, rt_packs.signed_crc(data), len(data), len(data), len(data),
       name, rt_packs.signed_crc(data), len(data))
        (self.project / "testplay.sk").write_text(script, encoding="utf-8")
        env = os.environ.copy()
        env.update(TEMP=str(self.root / "os-temp"), TMP=str(self.root / "os-temp"),
                   APPDATA=str(self.root / "roaming"), LOCALAPPDATA=str(self.root / "local"))
        proc = subprocess.run([str(self.root / "rpgcobo.exe"), "-testplay"], cwd=self.root, env=env,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
        output = proc.stdout.decode("utf-8", errors="replace")
        self.assertIn("[PACK TEST] shard reuse OK", output, output)

    def test_fast_update_detects_same_size_corrupt_active_index(self):
        source = rt_packs.build(self.project, self.root / "output")
        rt_packs.install(self.root, source)
        active = self.project / "rtpacks" / "active.json"
        original = active.read_bytes()
        active.write_bytes(b"!" + original[1:])
        script = """
::RPGStage <- { launch = function(opt=null) {} };
::Rokugan <- {};
runsk("/plugin/rokugan/RokuganUpdate.sk");
local p = "_tools/rpgcobo-tool/project/rtpacks/active.json";
local remote = { files = {} };
remote.files[p] <- ["%s", %d];
local need = ::Rokugan.updScan(remote, null, true);
if (length(need) != 1 || need[0] != p) throw "corrupt index was skipped";
printf("[PACK TEST] corrupt index detected\\n");
skExit(0);
""" % (rt_packs.signed_crc(original), len(original))
        (self.project / "testplay.sk").write_text(script, encoding="utf-8")
        env = os.environ.copy()
        env.update(TEMP=str(self.root / "os-temp"), TMP=str(self.root / "os-temp"),
                   APPDATA=str(self.root / "roaming"), LOCALAPPDATA=str(self.root / "local"))
        proc = subprocess.run([str(self.root / "rpgcobo.exe"), "-testplay"], cwd=self.root, env=env,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
        output = proc.stdout.decode("utf-8", errors="replace")
        self.assertIn("[PACK TEST] corrupt index detected", output, output)

    def test_in_game_updater_stages_pack_before_activation(self):
        first = rt_packs.build(self.project, self.root / "output")
        self.download_update(first, prune=True)
        old_active = (self.project / "rtpacks" / "active.json").read_bytes()
        next_project = self.root / "next-project"
        next_assets = next_project / "resource" / "native_chara"
        (next_assets / "tex").mkdir(parents=True)
        for name in ("deduce_brush.mdl", "deduce_brush.pm"):
            shutil.copyfile(ENGINE / "project" / "resource" / "native_chara" / name, next_assets / name)
        new_texture = ENGINE / "project" / "resource" / "native_chara" / "tex" / "head_checks_normal.png"
        shutil.copyfile(new_texture, next_assets / "tex" / "head_checks_color.png")
        second = rt_packs.build(next_project, self.root / "output", previous=first)
        index_bytes = (second / "active.json").read_bytes()
        index = json.loads(index_bytes)
        self.assertEqual(len(index["packs"]), 1)
        pack_name = next(iter(index["packs"]))
        pack_bytes = (second / pack_name).read_bytes()
        active_path = "_tools/rpgcobo-tool/project/rtpacks/active.json"
        pack_path = f"_tools/rpgcobo-tool/project/rtpacks/{second.name}/{pack_name}"
        remote = {"version": 999, "files": {
            active_path: [rt_packs.signed_crc(index_bytes), len(index_bytes)],
            pack_path: [rt_packs.signed_crc(pack_bytes), len(pack_bytes)],
        }}
        server = self.root / "server"
        server.mkdir()
        (server / "active.json").write_bytes(index_bytes)
        (server / "remote.json").write_text(json.dumps(remote), encoding="utf-8")
        (server / "version.json").write_text('{"version":999}', encoding="utf-8")
        script = """
::RPGStage <- { launch = function(opt=null) {} };
::Rokugan <- {};
runsk("/plugin/rokugan/RokuganUpdate.sk");
::Rokugan.updShow = function(s) {};
::Rokugan.updGet = function(path) {
 if (path.endsWith("active.json")) return FileRef("server/active.json").load();
 if (path.endsWith(".pak")) return FileRef("server/pack.pak").load();
 if (path == "rt_manifest.json") return FileRef("server/remote.json").load();
 if (path == "version.json") return FileRef("server/version.json").load();
 throw "unexpected download";
};
local remote = decodeJSON(FileRef("server/remote.json").load());
local need = ["%s", "%s"];
local result = ::Rokugan.updApply(remote, need);
if (length(result.bad) != EXPECTED) throw "wrong updater result";
printf("[PACK TEST] apply complete\\n");
skExit(0);
""" % (active_path, pack_path)
        env = os.environ.copy()
        env.update(TEMP=str(self.root / "os-temp"), TMP=str(self.root / "os-temp"),
                   APPDATA=str(self.root / "roaming"), LOCALAPPDATA=str(self.root / "local"))

        def apply(expected):
            (self.project / "testplay.sk").write_text(script.replace("EXPECTED", str(expected)), encoding="utf-8")
            proc = subprocess.run([str(self.root / "rpgcobo.exe"), "-testplay"], cwd=self.root, env=env,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
            output = proc.stdout.decode("utf-8", errors="replace")
            self.assertIn("[PACK TEST] apply complete", output, output)

        (server / "pack.pak").write_bytes(pack_bytes[:-1])
        apply(1)
        self.assertEqual((self.project / "rtpacks" / "active.json").read_bytes(), old_active)
        (server / "pack.pak").write_bytes(pack_bytes)
        invalid_index = dict(index)
        invalid_index["generation"] = "../invalid"
        invalid_bytes = json.dumps(invalid_index).encode()
        (server / "active.json").write_bytes(invalid_bytes)
        remote["files"][active_path] = [rt_packs.signed_crc(invalid_bytes), len(invalid_bytes)]
        (server / "remote.json").write_text(json.dumps(remote), encoding="utf-8")
        apply(1)
        self.assertEqual((self.project / "rtpacks" / "active.json").read_bytes(), old_active)
        (server / "active.json").write_bytes(index_bytes)
        remote["files"][active_path] = [rt_packs.signed_crc(index_bytes), len(index_bytes)]
        (server / "remote.json").write_text(json.dumps(remote), encoding="utf-8")
        apply(0)
        self.assertEqual((self.project / "rtpacks" / "active.json").read_bytes(), index_bytes)
        self.run_engine(rt_packs.signed_crc(new_texture.read_bytes()))

    def test_in_game_updater_bootstraps_loose_installation(self):
        source = rt_packs.build(self.project, self.root / "output")
        index_bytes = (source / "active.json").read_bytes()
        index = json.loads(index_bytes)
        name = next(iter(index["packs"]))
        data = (source / name).read_bytes()
        active_path = "_tools/rpgcobo-tool/project/rtpacks/active.json"
        pack_path = f"_tools/rpgcobo-tool/project/rtpacks/{source.name}/{name}"
        server = self.root / "server"
        server.mkdir()
        (server / "active.json").write_bytes(index_bytes)
        (server / "version.json").write_text('{"version":999}', encoding="utf-8")
        remote = {"version": 999, "files": {
            active_path: [rt_packs.signed_crc(index_bytes), len(index_bytes)],
            pack_path: [rt_packs.signed_crc(data), len(data)],
        }}
        (server / "remote.json").write_text(json.dumps(remote), encoding="utf-8")
        script = """
::RPGStage <- { launch = function(opt=null) {} };
::Rokugan <- {};
runsk("/plugin/rokugan/RokuganUpdate.sk");
::Rokugan.updShow = function(s) {};
::Rokugan.updGet = function(path) {
 if (path.endsWith("active.json")) return FileRef("server/active.json").load();
 if (path.endsWith(".pak")) return FileRef("server/pack.pak").load();
 if (path == "rt_manifest.json") return FileRef("server/remote.json").load();
 if (path == "version.json") return FileRef("server/version.json").load();
 throw "unexpected download";
};
local remote = decodeJSON(FileRef("server/remote.json").load());
local result = ::Rokugan.updApply(remote, ["%s", "%s"]);
if (length(result.bad) != EXPECTED) throw "wrong updater result";
printf("[PACK TEST] bootstrap apply OK\\n");
skExit(0);
""" % (active_path, pack_path)
        env = os.environ.copy()
        env.update(TEMP=str(self.root / "os-temp"), TMP=str(self.root / "os-temp"),
                   APPDATA=str(self.root / "roaming"), LOCALAPPDATA=str(self.root / "local"))

        def apply(expected):
            (self.project / "testplay.sk").write_text(script.replace("EXPECTED", str(expected)), encoding="utf-8")
            proc = subprocess.run([str(self.root / "rpgcobo.exe"), "-testplay"], cwd=self.root, env=env,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
            output = proc.stdout.decode("utf-8", errors="replace")
            self.assertIn("[PACK TEST] bootstrap apply OK", output, output)

        (server / "pack.pak").write_bytes(data[:-1])
        apply(1)
        self.assertFalse((self.project / "rtpacks" / "active.json").exists())
        self.assertTrue((self.assets / "deduce_brush.mdl").exists())
        (server / "pack.pak").write_bytes(data)
        apply(0)
        self.assertEqual((self.project / "rtpacks" / "active.json").read_bytes(), index_bytes)
        texture = self.assets / "tex" / "head_checks_color.png"
        crc = rt_packs.signed_crc(texture.read_bytes())
        self.run_engine(crc)
        for path in self.assets.rglob("*"):
            if path.is_file():
                path.unlink()
        self.run_engine(crc)

    def test_shipped_updater_can_install_compatible_release_and_recover(self):
        def shipped(name):
            result = subprocess.run(["git", "show", "119d6021:_tools/rpgcobo-tool/" + name],
                                    cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode:
                self.skipTest("shipped updater revision unavailable")
            return result.stdout

        old_boot = shipped("boot.sk")
        old_updater = shipped("project/plugin/rokugan/RokuganUpdate.sk")
        self.assertNotIn(b'runsk("/rt_pack.sk")', old_boot)
        shutil.copyfile(ENGINE / "project" / "sakana.proj", self.project / "sakana.proj")
        texture = self.assets / "tex" / "head_checks_color.png"
        previous_texture = texture.read_bytes()
        updated_texture = (ENGINE / "project" / "resource" / "native_chara" /
                           "tex" / "head_checks_normal.png").read_bytes()
        texture.write_bytes(updated_texture)
        source = rt_packs.build(self.project, self.root / "output")
        texture.write_bytes(previous_texture)
        index_bytes = (source / "active.json").read_bytes()
        index = json.loads(index_bytes)
        name = next(iter(index["packs"]))
        pack_bytes = (source / name).read_bytes()
        game = "_tools/rpgcobo-tool/"
        active_path = game + "project/rtpacks/active.json"
        pack_path = game + f"project/rtpacks/{source.name}/{name}"
        payloads = {
            game + "boot.sk": (ENGINE / "boot.sk").read_bytes(),
            game + "project/rt_pack.sk": (ENGINE / "project" / "rt_pack.sk").read_bytes(),
            game + "project/plugin/rokugan/RokuganUpdate.sk":
                (ENGINE / "project" / "plugin" / "rokugan" / "RokuganUpdate.sk").read_bytes(),
            game + "project/resource/native_chara/tex/head_checks_color.png": updated_texture,
            active_path: index_bytes,
            pack_path: pack_bytes,
        }
        for tool in rt_packs.CUTOVER_TOOLS:
            payloads[game + "rtpack-tools/" + tool] = (ROOT / "tools" / tool).read_bytes()
        payloads[game + "rtpack-tools/loader.sha256"] = rt_packs.digest(
            (ENGINE / "project" / "rt_pack.sk").read_bytes()).encode()
        remote = {"version": 999, "files": {
            path: [rt_packs.signed_crc(data), len(data)] for path, data in payloads.items()
        }}
        server = self.root / "server"
        for path, data in payloads.items():
            target = server.joinpath(*path.split("/"))
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        server.mkdir(exist_ok=True)
        (server / "rt_manifest.json").write_text(json.dumps(remote), encoding="utf-8")
        (server / "version.json").write_text('{"version":999}', encoding="utf-8")
        (self.root / "boot.sk").write_bytes(old_boot)
        updater = self.project / "plugin" / "rokugan" / "RokuganUpdate.sk"
        updater.write_bytes(old_updater)
        script = """
::RPGStage <- { launch = function(opt=null) {} };
::Rokugan <- {};
runsk("/plugin/rokugan/RokuganUpdate.sk");
::Rokugan.updShow = function(s) {};
::Rokugan.updGet = function(path) { return FileRef("server/" .. path).load(); };
local remote = decodeJSON(FileRef("server/rt_manifest.json").load());
local result = ::Rokugan.updApply(remote, %s);
if (length(result.bad) != EXPECTED) throw "wrong updater result";
printf("[PACK TEST] legacy apply OK\\n");
skExit(0);
""" % json.dumps(list(payloads))
        env = os.environ.copy()
        env.update(TEMP=str(self.root / "os-temp"), TMP=str(self.root / "os-temp"),
                   APPDATA=str(self.root / "roaming"), LOCALAPPDATA=str(self.root / "local"))

        def apply(expected):
            (self.project / "testplay.sk").write_text(script.replace("EXPECTED", str(expected)), encoding="utf-8")
            proc = subprocess.run([str(self.root / "rpgcobo.exe"), "-testplay"], cwd=self.root, env=env,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=30)
            output = proc.stdout.decode("utf-8", errors="replace")
            self.assertIn("[PACK TEST] legacy apply OK", output, output)

        remote_pack = server.joinpath(*pack_path.split("/"))
        remote_pack.write_bytes(pack_bytes[:-1])
        apply(1)
        self.assertTrue((self.assets / "deduce_brush.mdl").exists())
        self.assertEqual(texture.read_bytes(), updated_texture)
        crc = rt_packs.signed_crc(updated_texture)
        self.run_engine(crc, mounted=False)
        remote_pack.write_bytes(pack_bytes)
        apply(0)
        self.run_engine(crc)
        self.assertTrue((self.assets / "deduce_brush.mdl").exists())
        self.assertTrue((self.root / "rtpack-tools" / "rt_pack_cutover.py").is_file())


if __name__ == "__main__":
    unittest.main()
