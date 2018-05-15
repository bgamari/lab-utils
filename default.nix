{ nixpkgs ? (import <nixpkgs> {}), pythonPackages ? nixpkgs.python3Packages }:

pythonPackages.buildPythonPackage {
  pname = "rtb-utils";
  version = "0.1";
  src = ./.;
  propagatedBuildInputs = with pythonPackages; [ vxi11 numpy scipy matplotlib ];
}
