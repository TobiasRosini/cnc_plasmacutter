#!/usr/bin/env python3
"""
Führt ein CAD-Skript im laufenden FreeCAD aus (RPC-Server des MCP-Addons,
Port 9875), sonst headless per Flatpak-FreeCADCmd.

  python3 cad/live.py cad/wanne/wanne.py [weitere Skripte ...]
"""
import os
import subprocess
import sys
import xmlrpc.client

RPC = "http://127.0.0.1:9875"
CAD = os.path.dirname(os.path.abspath(__file__))


def live(skript):
    code = (
        "import sys, importlib\n"
        f"sys.path.insert(0, {CAD!r})\n"
        f"sys.path.insert(0, {os.path.dirname(skript)!r})\n"
        "import fc_dok; importlib.reload(fc_dok)\n"
        f"exec(compile(open({skript!r}).read(), {skript!r}, 'exec'), "
        f"{{'__file__': {skript!r}, '__name__': '__main__'}})\n"
    )
    s = xmlrpc.client.ServerProxy(RPC, allow_none=True)
    r = s.execute_code(code)
    print(r.get("message", r))
    return bool(r.get("success"))


def headless(skript):
    r = subprocess.run(["flatpak", "run", "--command=FreeCADCmd",
                        "org.freecad.FreeCAD", skript],
                       capture_output=True, text=True)
    fehler = [z for z in (r.stdout + r.stderr).splitlines()
              if "Error" in z or "Exception" in z or "Traceback" in z]
    print("\n".join(fehler) or "headless ok")
    return not fehler


def main():
    try:
        xmlrpc.client.ServerProxy(RPC).ping()
        lauf = live
        print("FreeCAD offen: live")
    except Exception:
        lauf = headless
        print("FreeCAD nicht erreichbar: headless")
    ok = True
    for a in sys.argv[1:]:
        ok &= lauf(os.path.abspath(a))
    sys.exit(0 if ok else 1)


main()
