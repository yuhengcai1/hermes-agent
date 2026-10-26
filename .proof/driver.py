
import os, shutil, subprocess, sys, tempfile, json
from pathlib import Path
root = Path(tempfile.mkdtemp())
sysdir = Path(os.environ["SystemRoot"]) / "System32"
ps = sysdir / "WindowsPowerShell" / "v1.0" / "powershell.exe"
def build(out, tag):
    src = 'public static class P { public static int Main(string[] a){ System.IO.File.AppendAllText(System.IO.Path.Combine(System.Environment.CurrentDirectory, "ran.txt"), "%s\\n"); System.Console.WriteLine("%s"); return 0; } }' % (tag, tag)
    subprocess.run([str(ps), "-NoProfile", "-Command", f"Add-Type -TypeDefinition '{src}' -OutputAssembly '{out}' -OutputType ConsoleApplication"], check=True)
planted = root / "repo"; planted.mkdir()
pathdir = root / "bin"; pathdir.mkdir()
build(str(planted / "taskkill.exe"), "PLANTED")
for n in ("powershell.exe", "probe.exe", "whoami.exe", "cmd.exe", "tasklist.exe", "where.exe"):
    shutil.copy(planted / "taskkill.exe", planted / n)
build(str(pathdir / "probe.exe"), "PATHCOPY")
code = r"""
import subprocess, sys, shutil, json, os
res = {}
for name in ("taskkill", "powershell", "probe", "whoami", "cmd", "tasklist", "where", "taskkill.exe"):
    try:
        r = subprocess.run([name, "/?"], capture_output=True, text=True, timeout=30, stdin=subprocess.DEVNULL)
        out = (r.stdout or "").strip().splitlines()
        res[name] = out[0][:60] if out else f"rc={r.returncode}"
    except Exception as e:
        res[name] = "ERR " + repr(e)[:80]
    res["which:" + name] = shutil.which(name)
print(json.dumps({"py": sys.version.split()[0], "switch": "NODEFAULTCURRENTDIRECTORYINEXEPATH" in {k.upper() for k in os.environ}, "res": res}))
"""
for py in sys.argv[1:]:
    for switch in (False, True):
        env = {k: v for k, v in os.environ.items() if k.upper() != "NODEFAULTCURRENTDIRECTORYINEXEPATH"}
        env["PATH"] = str(pathdir) + os.pathsep + env["PATH"]
        if switch:
            env["NoDefaultCurrentDirectoryInExePath"] = "1"
        r = subprocess.run([py, "-c", code], cwd=planted, env=env, capture_output=True, text=True, timeout=300)
        print("RESULT", py, switch, r.stdout.strip(), r.stderr.strip()[-400:])
