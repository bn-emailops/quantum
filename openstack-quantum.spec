%if ! (0%{?fedora} > 12 || 0%{?rhel} > 5)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%endif


Name:		openstack-quantum
Version:	2012.1
Release:	b3003
Epoch:      1
Summary:	Virtual network service for OpenStack (quantum)

Group:		Applications/System
License:	ASL 2.0
URL:		http://launchpad.net/quantum/
Source0:	http://launchpad.net/quantum/essex/2012.1/+download/%{name}-%{version}.tar.gz
Source1:	quantum-server.init
Source2:	quantum.logrotate
Source3:	plugins.ini
Source4:	cisco_plugins.ini
Source5:	credentials.ini
Source6:	db_conn.ini
Source7:	l2network_plugin.ini
Source8:	nexus.ini
Source9:	ucs.ini
Source10:	ovs_quantum_plugin.ini
Source11:	quantum.conf
Source12:	quantum.conf.test

BuildArch:	noarch

BuildRequires:	python-setuptools
#BuildRequires:	systemd-units
BuildRequires:	dos2unix

Requires:	python-quantum = %{epoch}:%{version}-%{release}
Requires:	python-cheetah

Requires(pre):	shadow-utils
#Requires(post): systemd-units
#Requires(preun): systemd-units
#Requires(postun): systemd-units


%description
Quantum is a virtual network service for Openstack, and a part of
Netstack. Just like OpenStack Nova provides an API to dynamically
request and configure virtual servers, Quantum provides an API to
dynamically request and configure virtual networks. These networks
connect "interfaces" from other OpenStack services (e.g., virtual NICs
from Nova VMs). The Quantum API supports extensions to provide
advanced network capabilities (e.g., QoS, ACLs, network monitoring,
etc.)


%package -n python-quantum
Summary:	Quantum Python libraries
Group:		Applications/System

Requires:	MySQL-python
Requires:	python-configobj
Requires:	python-eventlet
Requires:	python-gflags
Requires:	python-anyjson
Requires:	python-nose
Requires:	python-paste-deploy >= 1.5.0
Requires:	python-routes
Requires:	python-sqlalchemy
Requires:	python-webob
Requires:	python-webtest
#Requires:	openvswitch
Requires:	tunctl
Requires:       python-quantumclient

%description -n python-quantum
Quantum provides an API to dynamically request and configure virtual
networks.

This package contains the quantum Python library.


%prep
rm -rf bin/__init__.py
rm -rf tools

%setup -q -n %{name}-%{version}


mv quantum/plugins/cisco/README README-cisco
chmod 644 README-cisco
dos2unix README-cisco
mv quantum/plugins/openvswitch/README README-openvswitch


%build
%{__python} setup.py build


%install
rm -rf %{buildroot}

%{__python} setup.py install -O1 --skip-build --root %{buildroot}

# Remove docs since they don't build
rm -rf %{buildroot}%{python_sitelib}/doc

# Install execs with reasonable names
install -p -D -m 755 bin/quantum-server %{buildroot}%{_bindir}/quantum-server
install -d -m 755 %{buildroot}%{_bindir}/quantum-cli

#locks
install -d -m 755 %{buildroot}%{_localstatedir}/run/quantum

#init.d
install -p -D -m 755 %{SOURCE1} %{buildroot}%{_initrddir}/quantum-server


# Install config files, relocating ini files to /etc/quantum
install -p -D -m 644 %{SOURCE3} %{buildroot}%{_sysconfdir}/quantum/plugins.ini
install -p -D -m 644 %{SOURCE4} %{buildroot}%{_sysconfdir}/quantum/plugins/cisco/cisco_plugins.ini
install -p -D -m 644 %{SOURCE5} %{buildroot}%{_sysconfdir}/quantum/plugins/cisco/credentials.ini
install -p -D -m 644 %{SOURCE6} %{buildroot}%{_sysconfdir}/quantum/plugins/cisco/db_conn.ini
install -p -D -m 644 %{SOURCE7} %{buildroot}%{_sysconfdir}/quantum/plugins/cisco/l2network_plugin.ini
install -p -D -m 644 %{SOURCE8} %{buildroot}%{_sysconfdir}/quantum/plugins/cisco/nexus.ini
install -p -D -m 644 %{SOURCE9} %{buildroot}%{_sysconfdir}/quantum/plugins/cisco/ucs.ini
install -p -D -m 644 %{SOURCE10} %{buildroot}%{_sysconfdir}/quantum/plugins/openvswitch/ovs_quantum_plugin.ini
install -p -D -m 644 %{SOURCE11} %{buildroot}%{_sysconfdir}/quantum/quantum.conf
install -p -D -m 644 %{SOURCE12} %{buildroot}%{_sysconfdir}/quantum/quantum.conf.test


# Install logrotate
install -p -D -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/openstack-quantum

# Setup directories
install -d -m 755 %{buildroot}%{_sharedstatedir}/quantum
install -d -m 755 %{buildroot}%{_localstatedir}/log/quantum


%pre
getent group quantum >/dev/null || groupadd -r quantum --gid 164
getent passwd quantum >/dev/null || \
    useradd --uid 164 -r -g quantum -d %{_sharedstatedir}/quantum -s /sbin/nologin \
    -c "OpenStack Quantum Daemons" quantum
exit 0


%post
if [ $1 -eq 1 ] ; then
    # Initial installation
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi


%preun
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /bin/systemctl --no-reload disable openstack-quantum.service > /dev/null 2>&1 || :
    /bin/systemctl stop openstack-quantum.service > /dev/null 2>&1 || :
fi


%postun
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # Package upgrade, not uninstall
    /bin/systemctl try-restart openstack-quantum.service >/dev/null 2>&1 || :
fi


%files
%doc LICENSE
%doc README
%doc README-cisco
%doc README-openvswitch
%{_bindir}/*
#%{_unitdir}/*
%{_initrddir}/quantum-server
%dir %{_sysconfdir}/quantum
%config(noreplace) %{_sysconfdir}/logrotate.d/openstack-quantum
%config(noreplace) %{_sysconfdir}/quantum/plugins.ini
%config(noreplace) %{_sysconfdir}/quantum/plugins/cisco/cisco_plugins.ini
%config(noreplace) %{_sysconfdir}/quantum/plugins/cisco/credentials.ini
%config(noreplace) %{_sysconfdir}/quantum/plugins/cisco/db_conn.ini
%config(noreplace) %{_sysconfdir}/quantum/plugins/cisco/l2network_plugin.ini
%config(noreplace) %{_sysconfdir}/quantum/plugins/cisco/nexus.ini
%config(noreplace) %{_sysconfdir}/quantum/plugins/cisco/ucs.ini
%config(noreplace) %{_sysconfdir}/quantum/plugins/openvswitch/ovs_quantum_plugin.ini
%config(noreplace) %{_sysconfdir}/quantum/quantum.conf
%config(noreplace) %{_sysconfdir}/quantum/quantum.conf.test
%dir %attr(0755, quantum, quantum) %{_sharedstatedir}/quantum
%dir %attr(0755, quantum, quantum) %{_localstatedir}/log/quantum
%dir %attr(0755, quantum, quantum) %{_localstatedir}/run/quantum

%files -n python-quantum
%doc LICENSE
%{python_sitelib}/quantum
%{python_sitelib}/quantum-*.egg-info


%changelog
* Thu Nov  18 2011 Robert Kukura <rkukura@redhat.com> - 2011.3-1
- Initial package for Fedora
