{ buildPythonPackage, vxi11, numpy, scipy, matplotlib }:

buildPythonPackage {
  pname = "rtb-utils";
  version = "0.1";
  src = ./.;
  propagatedBuildInputs = [ vxi11 numpy scipy matplotlib ];
}
