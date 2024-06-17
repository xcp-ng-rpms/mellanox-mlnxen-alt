%define vendor_name Mellanox
%define vendor_label mellanox
%define driver_name mlnxen

# XCP-ng: install to the override directory
%define module_dir override

Summary: %{vendor_name} %{driver_name} device drivers
Name: %{vendor_label}-%{driver_name}-alt
Version: 5.9_0.5.5.0
Release: 1.2%{?dist}
License: GPLv2

# Extracted from latest XS driver disk
Source0: mellanox-mlnxen-5.9_0.5.5.0.tar.gz

BuildRequires: gcc
BuildRequires: kernel-devel
Provides: vendor-driver
Requires: kernel-uname-r = %{kernel_version}
Requires(post): /usr/sbin/depmod
Requires(postun): /usr/sbin/depmod

# XCP-ng: virtual provides for mlx4-modules-alt's need
# Versioned using the date in the compat_base file in the tarball
Provides: mlx_compat = 20230125

%description
%{vendor_name} %{driver_name} device drivers for the Linux Kernel
version %{kernel_version}.

%prep
%autosetup -p1 -n mellanox-mlnxen-%{version}

%build
export EXTRA_CFLAGS='-DVERSION=\"%version\"'
export KSRC=/lib/modules/%{kernel_version}/build
export KVERSION=%{kernel_version}

find compat -type f -exec touch -t 200012201010 '{}' \; || true
./scripts/mlnx_en_patch.sh --kernel $KVERSION --kernel-sources $KSRC %{?_smp_mflags}
%{__make} V=0 %{?_smp_mflags}

%install
export INSTALL_MOD_PATH=%{buildroot}
export INSTALL_MOD_DIR=%{module_dir}
export KSRC=/lib/modules/%{kernel_version}/build
export KVERSION=%{kernel_version}

%{__make} install KSRC=$KSRC MODULES_DIR=$INSTALL_MOD_DIR DESTDIR=%{buildroot} KERNELRELEASE=$KVERSION DEPMOD=/bin/true
# Cleanup unnecessary kernel-generated module dependency files.
find %{buildroot}/lib/modules -iname 'modules.*' -exec rm {} \;

# mark modules executable so that strip-to-file can strip them
find %{buildroot}/lib/modules/%{kernel_version} -name "*.ko" -exec mv '{}' %{buildroot}/lib/modules/%{kernel_version}/%{module_dir} \;
find %{buildroot}/lib/modules/%{kernel_version} -name "*.ko" -type f | xargs chmod u+x

%post
/sbin/depmod %{kernel_version}
%{regenerate_initrd_post}

%postun
/sbin/depmod %{kernel_version}
%{regenerate_initrd_postun}

%posttrans
%{regenerate_initrd_posttrans}

%files
/lib/modules/%{kernel_version}/*/*.ko

%changelog
* Mon Jun 17 2024 Samuel Verschelde <stormi-xcp@ylix.fr> - 5.9_0.5.5.0-1.2
- Add mlx_compat virtual provides, needed by mlx4-modules-alt

* Thu Sep 21 2023 Gael Duperrey <gduperrey@vates.tech> - 5.9_0.5.5.0-1.1
- Update to version 5.9_0.5.5.0-1.1
- Synced from XS driver SRPM mellanox-mlnxen-5.9_0.5.5.0-1.xs8~2_1.src.rpm
- *** Upstream changelog ***
- * Mon Aug 28 2023 Stephen Cheng <stephen.cheng@citrix.com> - 5.9_0.5.5.0-1
- - CP-43274: Update to version 5.9-0.5.5.0

* Tue Jan 10 2023 Samuel Verschelde <stormi-xcp@ylix.fr> - 5.4_1.0.3.0-1
- Initial package
