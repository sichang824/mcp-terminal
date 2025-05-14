{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  buildInputs = [
    pkgs.python3
    pkgs.uv
  ];

  shellHook = ''
    make setup
  '';
}