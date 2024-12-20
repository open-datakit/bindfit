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
    in {
      devShells.default = pkgs.mkShell {
        buildInputs = [
          pkgs.pre-commit
          pkgs.python310
          pkgs.python310Packages.numpy
          pkgs.python310Packages.scipy
          pkgs.python310Packages.pandas
        ];
      };
    });
}
