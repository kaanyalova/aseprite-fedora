Name:           aseprite
Version:        v1.3
%global _subver rc4
%global _skia_ver aseprite-m102 
%global _ver %{version}-%{_subver}



Release:        1%{?dist}
Summary:        Animated sprite editor & pixel art tool 



License:        CUSTOM
URL:            https://www.aseprite.org/

# fixed thumbnailer 
# see https://github.com/aseprite/aseprite/issues/3955
Source0: aseprite.thumbnailer 
#Source0:        https://github.com/aseprite/aseprite/releases/download/%version/Aseprite-%{version}-%{_subver}-Source.zip
#Source1:        https://github.com/aseprite/skia/archive/refs/tags/skia-%{_skia_tag}-%{_skiahash}.zip



# the ancient "recommended" clang10 package is so old that it refuses to install because llvm 10 is no longer in the repos

BuildRequires:  python git gcc-c++ clang libcxx-devel cmake ninja-build libX11-devel libXcursor-devel libXi-devel mesa-libGL-devel fontconfig-devel gn giflib-devel libjpeg-turbo-devel libcurl-devel cmark-devel zlib-devel  harfbuzz-devel pixman-devel freetype-devel gn 
# extra-cmake-modules kf5-kio-devel are needed for KDE thumbnailer



# tinyxml-devel 


# from the pkgbuild
Requires: libxcursor fontconfig hicolor-icon-theme libglvnd libcxx



%description    
Animated sprite editor & pixel art tool 


%prep

# the build flags from rpmbuild causes issues
# it is not mentioned anywhere in the docs of rpmbuild and it was very annoying to figure out what was causing the build to fail
# https://src.fedoraproject.org/rpms/redhat-rpm-config/blob/rawhide/f/buildflags.md
%undefine _auto_set_build_flags


# disable build ids because there is no debug package s
# https://github.com/rpm-software-management/rpm/blob/4a9440006398646583f0d9ae1837dad2875013aa/macros.in#L506
%global _build_id_links none




# Build Flags

# uses prebuilt skia instead of building from source
# this doesn't work with aseprites releases because it is built with ubuntu 18.04
%global prebuilt_skia 0
%global prebuilt_skia_url https://github.com/aseprite/skia/releases/download/m102-861e4743af/Skia-Linux-Release-x64-libstdc++.zip 

# removes build dirs after build
%global clean_build 1

# uses system gn in enabled, downloads gn otherwise
%global use_gn_package 1

# version and hash of skia's source
%global _skiaver m102





# https://stackoverflow.com/questions/36498981/shell-dont-fail-git-clone-if-folder-already-exists
git -C aseprite pull || git clone --depth 1 -b %{_ver} https://github.com/aseprite/aseprite
env -C aseprite/ git submodule update --init --recursive --depth 1



mkdir -p deps


%if %{prebuilt_skia} == 0

	%if %{use_gn_package} == 0
		# Download depot tools and add to path
		git -C deps/depot_tools pull || git -C deps/ clone https://chromium.googlesource.com/chromium/tools/depot_tools.git
		%global gn_dir %{_builddir}/deps/depot_tools/gn
	%endif 

	%if %{use_gn_package} == 1
		%global gn_dir /usr/bin/gn
	%endif


	git -C deps/skia pull || git -C deps/ clone -b %{_skia_ver} --depth 1 https://github.com/aseprite/skia.git 
	env -C deps/skia python tools/git-sync-deps
	%endif


	# prebuilt skia
	%if %{prebuilt_skia} == 1
		# skip downloading if the folder exists
		if [ ! -d deps/skia-prebuilt ]; then
		curl -Li -C - %{prebuilt_skia_url} --output deps/skia.zip
		# unzip somehow returns with 1 but with no error messages even though it successfully extracts the files
		# we just ignore the error, what could go wrong
		unzip -n deps/skia.zip -d deps/skia-prebuilt || true
		rm -rf deps/skia.zip
		fi
	%endif 

	    
%build


	# set the skia dirs 
	%if %{prebuilt_skia} == 1 
		%global _skia_dir deps/skia-prebuilt
		%global _skia_out_dir deps/skia-prebuilt/out/Release-x64
	%endif 

	%if %{prebuilt_skia} == 0
		%global _skia_dir deps/skia
		%global _skia_out_dir deps/skia/out/Release-x64



%endif 


# build skia
%if %{prebuilt_skia} == 0 
	#export CXX=clang++
	#export CC=clang
	#export LD=lld
	#export AR=ar
	#export NM=nm


	env -C %{_skia_dir} %{gn_dir} gen out/Release-x64 --args='is_debug=false is_official_build=true skia_use_system_expat=false skia_use_system_icu=false skia_use_system_libjpeg_turbo=false skia_use_system_libpng=false skia_use_system_libwebp=false skia_use_system_zlib=false skia_use_sfntly=false skia_use_freetype=true skia_use_harfbuzz=true skia_pdf_subset_harfbuzz=true skia_use_system_freetype2=false skia_use_system_harfbuzz=false cc="clang" cxx="clang++" extra_cflags_cc=["-stdlib=libc++"] extra_ldflags=["-stdlib=libc++"]'


	ninja -C %{_skia_dir}/out/Release-x64 skia modules
%endif





# build aseprite
mkdir -p aseprite/build

export CC=clang
export CXX=clang++

# link to shared libraries if possible
# but it can get removed altogether https://github.com/aseprite/aseprite/issues/2843
cmake -S aseprite -B aseprite/build \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DCMAKE_CXX_FLAGS:STRING=-stdlib=libc++ \
  -DCMAKE_EXE_LINKER_FLAGS:STRING=-stdlib=libc++ \
  -DLAF_BACKEND=skia \
  -DSKIA_DIR=%{_skia_dir} \
  -DSKIA_LIBRARY_DIR=%{_skia_out_dir} \
  -DSKIA_LIBRARY=%{_skia_out_dir}/libskia.a \
  -DUSE_SHARED_CMARK=on \
  -DUSE_SHARED_CURL=on \
  -DUSE_SHARED_GIFLIB=on \
  -DUSE_SHARED_JPEGLIB=on \
  -DUSE_SHARED_ZLIB=on \
  -DUSE_SHARED_LIBPNG=on \
  -DUSE_SHARED_PIXMAN=on \
  -DUSE_SHARED_FREETYPE=on \
  -DUSE_SHARED_HARFBUZZ=on \
  -G Ninja

  
# -DUSE_SHARED_TINYXML=on 
# does not build ,see https://github.com/aseprite/aseprite/issues/1146 for similar issue on void linux

ninja -C aseprite/build aseprite




%install
%global aseprite_out aseprite/build/bin


rm -rf $RPM_BUILD_ROOT

# install the binary
mkdir -p $RPM_BUILD_ROOT/usr/bin
cp %{aseprite_out}/aseprite $RPM_BUILD_ROOT/usr/bin

# install the .desktop file
mkdir -p $RPM_BUILD_ROOT/usr/share/applications
cp aseprite/src/desktop/linux/aseprite.desktop $RPM_BUILD_ROOT/usr/share/applications

# install mime types
mkdir -p $RPM_BUILD_ROOT/usr/share/mime/packages
cp aseprite/src/desktop/linux/mime/aseprite.xml $RPM_BUILD_ROOT/usr/share/mime/packages

# install icons 
# they aren't standart linux icons so use the script i took from the aur package 
# https://aur.archlinux.org/cgit/aur.git/tree/PKGBUILD?h=aseprite



for _size in 16 32 48 64 128 256; do
	mkdir -p $RPM_BUILD_ROOT/usr/share/icons/hicolor/${_size}x${_size}/apps
	# The installed icon's name is taken from the `.desktop` file
	cp %{aseprite_out}/data/icons/ase$_size.png $RPM_BUILD_ROOT/usr/share/icons/hicolor/${_size}x${_size}/apps/aseprite.png
done		


# remove the duplicate icons from the package
rm -rf $RPM_BUILD_ROOT/usr/share/aseprite/data/icons


# install the data
# here are the valid paths  https://github.com/aseprite/aseprite/blob/8b747b4d09c2802534cf93f95f50978a1eae8485/src/app/resource_finder.cpp#L115 
mkdir -p $RPM_BUILD_ROOT/usr/share/aseprite
cp -r %{aseprite_out}/data $RPM_BUILD_ROOT/usr/share/aseprite



# install the thumbnailer binary 
cp aseprite/src/desktop/linux/aseprite-thumbnailer $RPM_BUILD_ROOT/usr/bin

# install the "GNOME" thumbnailer,
# the original aseprite.thumbnailer thumbnails a lot of image formats for no reason, this package uses a modified one which only thumbnails .ase files
# it doesn't work on KDE and it needs a separate library to be build, which has a lot of dependencies, i might make a package for KDE thumbnailer later (probably not)
mkdir -p $RPM_BUILD_ROOT/usr/share/thumbnailers
cp $RPM_SOURCE_DIR/aseprite.thumbnailer $RPM_BUILD_ROOT/usr/share/thumbnailers




%files
/usr/bin/aseprite
/usr/bin/aseprite-thumbnailer
/usr/share/applications/aseprite.desktop
/usr/share/aseprite
/usr/share/icons/hicolor/**/apps/aseprite.png
/usr/share/mime/packages/aseprite.xml
/usr/share/thumbnailers/aseprite.thumbnailer
%license aseprite/EULA.txt
%license aseprite/docs/LICENSES.md



#%doc add-docs-here

%clean
%if %{clean_build} == 1 
rm -rf deps
rm -rf aseprite
%endif



%changelog
* Tue Jul 11 2023 kaanyalova <76952012+kaanyalova@users.noreply.github.com>
- 

