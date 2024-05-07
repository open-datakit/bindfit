{
  description = "";

  # Use the unstable nixpkgs to use the latest set of Python packages
  inputs.nixpkgs.url = "github:NixOS/nixpkgs/master";

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }:
    flake-utils.lib.eachDefaultSystem
    (system: let
      pkgs = import nixpkgs {
        inherit system;
      };

      opendatafit = pkgs.python3Packages.buildPythonPackage rec {
        name = "opendatafit";
        version = "db7b0801336f7011c2f14317cae499965df528b0";
        format = "pyproject";

        src = pkgs.fetchFromGitHub {
           owner = "opendatafit";
           repo = "${name}";
           rev = "${version}";
           sha256 = "12v79gwp7kr1di53kwfq09wsmp5mzh3dd58zx221slb6sdcgnnjr";
        };

        buildInputs = with pkgs.python3Packages; [
          setuptools
        ];

        propagatedBuildInputs = with pkgs.python3Packages; [
          pandas
        ];
      };

    in {
      devShells.default = pkgs.mkShell {
        buildInputs = [
          opendatafit
          pkgs.pre-commit
          pkgs.python311
          pkgs.python311Packages.numpy
          pkgs.python311Packages.scipy
          pkgs.python311Packages.pandas
        ];
      };
    });
}
