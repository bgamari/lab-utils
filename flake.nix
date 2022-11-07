{
  inputs.flake-utils.url = "github:numtide/flake-utils";

  outputs = { nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let pkgs = import nixpkgs {inherit system;};
      in rec {
        packages.rtb-utils = pythonPackages.callPackage ./default.nix {};
        devShells.default = pkgs.mkShell {
          buildInputs = [ packages.rtb-utils pythonPackages.ipython ];
        };
      });
}
