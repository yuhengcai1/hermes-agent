"""wine2e probe: does `powershell -File script.ps1` hold the script file while it runs?"""
import os, subprocess, sys, tempfile, time, pathlib
d = pathlib.Path(os.environ.get("RUNNER_TEMP", tempfile.gettempdir())) / "ps1hold"
d.mkdir(parents=True, exist_ok=True)
s = d / "windows.ps1"
s.write_text("Start-Sleep -Seconds 15\n", encoding="utf-8")
p = subprocess.Popen(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(s)])
time.sleep(5)
res = {}
for name, op in (("open_write", lambda: open(s, "r+b").close()),
                 ("rename", lambda: (os.rename(s, d / "moved.ps1"), os.rename(d / "moved.ps1", s))),
                 ("unlink_recreate", lambda: (os.unlink(s), s.write_text("x", encoding="utf-8")))):
    try:
        op(); res[name] = "ok"
    except OSError as e:
        res[name] = f"{type(e).__name__} winerror={getattr(e, 'winerror', None)}"
p.wait(timeout=60)
print("RESULT ps1-hold", res, flush=True)
