{ buildPythonPackage, setuptools, vxi11, numpy, scipy, matplotlib }:

buildPythonPackage {
  name = "rtb-utils";
  version = "0.1";
  format = "pyproject";
  src = ./.;
  propagatedBuildInputs = [ vxi11 numpy scipy matplotlib ];
  nativeBuildInputs = [ setuptools ];
}
