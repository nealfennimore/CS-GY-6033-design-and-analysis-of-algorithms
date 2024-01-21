{ pkgs ? import <nixpkgs> { } }:
with pkgs;
mkShell {
  buildInputs = [
    python3Packages.virtualenv
    python3Packages.jupyter
    python3Packages.ipykernel
    python3Packages.matplotlib
    python3Packages.pandas
    python3Packages.tabulate
    python3Packages.debugpy
  ];

  shellHook = ''
    [[ ! -d .venv ]] && python -m venv .venv
    source .venv/bin/activate
    export LD_LIBRARY_PATH=${stdenv.cc.cc.lib}/lib/:/run/opengl-driver/lib/
    if [[ -f requirements.txt ]]; then
      pip install -r requirements.txt --require-virtualenv
    fi
  '';

  packages = [
    python3Full
    texlive.combined.scheme-full
    # wkhtmltopdf
  ];
}
