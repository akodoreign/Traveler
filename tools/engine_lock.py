"""Shared engine launch for the test tools. rpgcobo.exe is single-instance: a second copy exits at once with code 7 and
prints nothing. So a launcher waits until no rpgcobo.exe runs, launches, and retries when it lost the race. It never
kills an engine it didn't start (the user's game and other agents' runs are rpgcobo.exe too): only its own Popen PID.

    import engine_lock
    proc = engine_lock.launch(args, cwd=TOOL, log=path)       # log: a path (opened "w"), an open file, or None
    ...
    engine_lock.stop(proc)
"""
import subprocess
import time


def running():
    """True while any rpgcobo.exe is running."""
    r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq rpgcobo.exe", "/NH"], capture_output=True, text=True)
    return "rpgcobo.exe" in r.stdout.lower()


def wait_free(poll=0.3, quiet=False, timeout=None):
    """Waits until no rpgcobo.exe is running. Returns False if timeout (seconds) ran out first."""
    t0, said = time.time(), False
    while running():
        if not quiet and not said:
            print("(waiting: another rpgcobo.exe is running)")
            said = True
        if timeout is not None and time.time() - t0 > timeout:
            return False
        time.sleep(poll)
    return True


def launch(args, cwd=None, log=None, tries=5, **kw):
    """Waits for a free engine, then starts args. A copy that exits with code 7 within ~2 s lost the race to
    another instance: wait and retry (up to tries times). Returns the Popen."""
    for t in range(tries):
        wait_free()
        if isinstance(log, str):
            out = open(log, "w")
        else:
            out = log
        kw2 = dict(kw)
        if out is not None:
            kw2.setdefault("stdout", out)
            kw2.setdefault("stderr", subprocess.STDOUT)
        proc = subprocess.Popen(args, cwd=cwd, **kw2)
        t0 = time.time()
        while time.time() - t0 < 2.0 and proc.poll() is None:
            time.sleep(0.1)
        if proc.poll() == 7:
            if isinstance(log, str):
                out.close()
            print("(rpgcobo.exe exited with 7: another instance won; retry %d)" % (t + 1))
            time.sleep(1.0)
            continue
        return proc
    raise RuntimeError("rpgcobo.exe would not start (another instance kept running)")


def stop(proc):
    """Ends this launcher's own engine (never any other)."""
    if proc is not None and proc.poll() is None:
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/F"], capture_output=True)
