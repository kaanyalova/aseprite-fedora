# aseprite-fedora

Fedora rpm package for aseprite

## How to install

Download the latest src.rpm from [Releases](https://github.com/kaanyalova/aseprite-fedora/releases)

Install `rpmbuild` required to build the package

```sh
sudo dnf install fedora-packager
```

Setup `rpmbuild` directories, this will create a folder called `rpmbuild` on your `$HOME` ([this can be changed](https://unix.stackexchange.com/a/553187))

```sh
rpmdev-setuptree
```

Install the build dependencies of the source package, replace the package name if needed

```sh
sudo dnf buildep aseprite-v1.3-1.fc39.src.rpm
```

Build the package, this may take quite a long time

```sh
rpmbuild --rebuild aseprite-v1.3-1.fc39.src.rpm
```

Install the built package it should be on the `RPMS` subdirectory of your rpmbuild folder

```sh
sudo dnf install ~/rpmbuild/RPMS/aseprite-v1.3-1.fc39.x86_64.rpm

```

## Distributing

Do not distribute the built RPM packages, it is against the [aseprite's EULA](https://github.com/aseprite/aseprite/blob/main/EULA.txt), distributing SRC.RPMs should be fine as all of the source code is downloaded when building.

## Support the aseprite devs

https://www.aseprite.org/#buy
