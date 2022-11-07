{
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let pkgs = import nixpkgs {inherit system;};
      in rec {
        packages.rtb-utils = pkgs.python3Packages.callPackage ./default.nix { };
        packages.default = packages.rtb-utils;
        devShells.default = pkgs.mkShell {
          buildInputs =
            let python = pkgs.python3.withPackages (ps: [ ps.ipython packages.rtb-utils ]);
            in [python];
        };
      });
}
