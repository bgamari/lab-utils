{
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let pkgs = import nixpkgs {inherit system;};
      in rec {
        packages.rtb-utils = pkgs.python3Packages.callPackage ./default.nix {
          matplotlib = pkgs.python3Packages.matplotlib.override { enableGtk3 = true; };
        };
        packages.default = packages.rtb-utils;
        devShells.default = pkgs.mkShell {
          buildInputs =
            let
              python = pkgs.python3.withPackages (ps: [
                packages.rtb-utils
                ps.ipython
                ps.jupyter
              ]);
            in [python];
        };
      });
}
