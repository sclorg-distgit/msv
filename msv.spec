%global pkg_name msv
%{?scl:%scl_package %{pkg_name}}
%{?java_common_find_provides_and_requires}

Name:          %{?scl_prefix}%{pkg_name}
Epoch:         1
Version:       2013.5.1
Release:       6.16%{?dist}
Summary:       Multi-Schema Validator
License:       BSD and ASL 1.1
URL:           http://msv.java.net/

# To generate tarball from upstream source control:
# $ ./create-tarball
Source0:       %{pkg_name}-%{version}-clean.tar.gz

# Parent POM is no longer in svn, get it from Maven central repository
Source1:       http://repo1.maven.org/maven2/net/java/dev/%{pkg_name}/%{pkg_name}-parent/2009.1/%{pkg_name}-parent-2009.1.pom

Source2:       http://www.apache.org/licenses/LICENSE-2.0.txt
Source3:       create-tarball.sh

# Use CatalogResolver from xml-commons-resolver package
Patch1:        %{pkg_name}-Use-CatalogResolver-class-from-xml-commons-resolver.patch

BuildRequires: %{?scl_prefix}javapackages-tools
BuildRequires: %{?scl_prefix}maven-local
BuildRequires: %{?scl_prefix_maven}maven-compiler-plugin
BuildRequires: %{?scl_prefix_maven}maven-install-plugin
BuildRequires: %{?scl_prefix_maven}maven-jar-plugin
BuildRequires: %{?scl_prefix_maven}maven-javadoc-plugin
BuildRequires: %{?scl_prefix_maven}maven-resources-plugin
BuildRequires: %{?scl_prefix_maven}maven-site-plugin
BuildRequires: %{?scl_prefix_maven}maven-surefire-plugin
BuildRequires: %{?scl_prefix_maven}maven-surefire-provider-junit
BuildRequires: %{?scl_prefix_maven}maven-plugin-build-helper
BuildRequires: %{?scl_prefix}isorelax
BuildRequires: %{?scl_prefix}isorelax-javadoc
BuildRequires: %{?scl_prefix}relaxngDatatype
BuildRequires: %{?scl_prefix}relaxngDatatype-javadoc
BuildRequires: %{?scl_prefix}xalan-j2
BuildRequires: %{?scl_prefix}xerces-j2
BuildRequires: %{?scl_prefix}junit
BuildRequires: %{?scl_prefix_maven}jvnet-parent
BuildRequires: %{?scl_prefix}xml-commons-resolver
BuildRequires: %{?scl_prefix}isorelax

BuildArch:     noarch


%description
The Sun Multi-Schema XML Validator (MSV) is a Java technology tool to validate
XML documents against several kinds of XML schemata. It supports RELAX NG,
RELAX Namespace, RELAX Core, TREX, XML DTDs, and a subset of XML Schema Part 1.
This latest (version 1.2) release includes several bug fixes and adds better
conformance to RELAX NG/W3C XML standards and JAXP masquerading.

%package       msv
Summary:       Multi-Schema Validator Core
# src/com/sun/msv/reader/xmlschema/DOMLSInputImpl.java is under ASL 2.0
# msv/src/com/sun/msv/writer/ContentHandlerAdaptor.java is partially under Public Domain
License:       BSD and ASL 1.1 and ASL 2.0 and Public Domain

%description   msv
%{summary}.

%package       rngconv
Summary:       Multi-Schema Validator RNG Converter

%description   rngconv
%{summary}.

%package       xmlgen
Summary:       Multi-Schema Validator Generator

%description    xmlgen
%{summary}.

%package       xsdlib
Summary:       Multi-Schema Validator XML Schema Library

%description   xsdlib
%{summary}.

%package       javadoc
Summary:       API documentation for Multi-Schema Validator
License:       BSD and ASL 1.1 and ASL 2.0 and Public Domain

%description   javadoc
%{summary}.

%package       manual
Summary:       Manual for Multi-Schema Validator
License:       BSD
Requires:       %{?scl_prefix}runtime

%description   manual
%{summary}.

%package       demo
Summary:       Samples for Multi-Schema Validator
License:       BSD
Requires:      %{?scl_prefix}msv-msv
Requires:      %{?scl_prefix}msv-xsdlib

%description   demo
%{summary}.

%prep
%setup -q -n %{pkg_name}-%{version}
%{?scl:scl enable %{scl_maven} %{scl} - <<"EOF"}
set -e -x

# We don't have this plugin
%pom_remove_plugin :buildnumber-maven-plugin

# Needed becuase of patch3
%pom_add_dep xml-resolver:xml-resolver

cp %{SOURCE1} parent-pom.xml

# ASL 2.0 license text
cp %{SOURCE2} Apache-LICENSE-2.0.txt

# Delete anything pre-compiled
find -name '*.class' -exec rm -f '{}' \;
find -name '*.jar' -exec rm -f '{}' \;
find -name '*.zip' -exec rm -f '{}' \;

# Delete class-path entries from manifests
for m in $(find . -name MANIFEST.MF) ; do
  sed --in-place -e '/^[Cc]lass-[Pp]ath:/d' $m
done

# Apply patches
%patch1 -p1

# Fix isorelax groupId
%pom_xpath_replace "pom:dependency[pom:groupId[text()='com.sun.xml.bind.jaxb']]/pom:groupId" "<groupId>isorelax</groupId>"
%pom_xpath_replace "pom:dependency[pom:groupId[text()='com.sun.xml.bind.jaxb']]/pom:groupId" "<groupId>isorelax</groupId>" generator
%pom_xpath_replace "pom:dependency[pom:groupId[text()='com.sun.xml.bind.jaxb']]/pom:groupId" "<groupId>isorelax</groupId>" msv
%pom_xpath_replace "pom:dependency[pom:groupId[text()='com.sun.xml.bind.jaxb']]/pom:groupId" "<groupId>isorelax</groupId>" rngconverter
%pom_xpath_replace "pom:dependency[pom:groupId[text()='com.sun.xml.bind.jaxb']]/pom:groupId" "<groupId>isorelax</groupId>" xsdlib

# Change encoding of non utf-8 files
for m in $(find . -name copyright.txt) ; do
  iconv -f iso-8859-1 -t utf-8 < $m > $m.utf8
  mv $m.utf8 $m
done

%mvn_file ":%{pkg_name}-core" %{pkg_name}-core %{pkg_name}-%{pkg_name}
%mvn_file ":%{pkg_name}-rngconverter" %{pkg_name}-rngconverter %{pkg_name}-rngconv
%mvn_file ":%{pkg_name}-generator" %{pkg_name}-generator %{pkg_name}-xmlgen
%mvn_file ":xsdlib" xsdlib %{pkg_name}-xsdlib

%mvn_alias ":xsdlib" "com.sun.msv.datatype.xsd:xsdlib"

%mvn_package ":%{pkg_name}" %{pkg_name}-msv
%mvn_package ":%{pkg_name}-core" %{pkg_name}-msv
%mvn_package ":%{pkg_name}-testharness" %{pkg_name}-msv
%mvn_package ":%{pkg_name}-rngconverter" %{pkg_name}-rngconv
%mvn_package ":%{pkg_name}-generator" %{pkg_name}-xmlgen
%mvn_package ":xsdlib" %{pkg_name}-xsdlib
%{?scl:EOF}

%build
%{?scl:scl enable %{scl_maven} %{scl} - <<"EOF"}
set -e -x
%mvn_build -s
%{?scl:EOF}

%install
%{?scl:scl enable %{scl_maven} %{scl} - <<"EOF"}
set -e -x
%mvn_install

# parent POM
install -pD -T -m 644 parent-pom.xml       %{buildroot}%{_mavenpomdir}/JPP-msv-parent.pom
%add_maven_depmap JPP-%{pkg_name}-parent.pom -f msv-xsdlib

# Manuals
install -d -m 755 %{buildroot}%{_docdir}/%{pkg_name}-%{version}/msv
install -m 644 msv/doc/*.html     %{buildroot}%{_docdir}/%{pkg_name}-%{version}/msv
install -m 644 msv/doc/*.gif      %{buildroot}%{_docdir}/%{pkg_name}-%{version}/msv
install -m 644 msv/doc/README.txt %{buildroot}%{_docdir}/%{pkg_name}-%{version}/msv

install -d -m 755 %{buildroot}%{_docdir}/%{pkg_name}-%{version}/rngconverter
install -m 644 rngconverter/README.txt %{buildroot}%{_docdir}/%{pkg_name}-%{version}/rngconverter

install -d -m 755 %{buildroot}%{_docdir}/%{pkg_name}-%{version}/generator
install -m 644 generator/*.html     %{buildroot}%{_docdir}/%{pkg_name}-%{version}/generator
install -m 644 generator/README.txt %{buildroot}%{_docdir}/%{pkg_name}-%{version}/generator

install -d -m 755 %{buildroot}%{_docdir}/%{pkg_name}-%{version}/xsdlib
install -m 644 xsdlib/*.html     %{buildroot}%{_docdir}/%{pkg_name}-%{version}/xsdlib
install -m 644 xsdlib/README.txt %{buildroot}%{_docdir}/%{pkg_name}-%{version}/xsdlib

# Examples
install -d -m 755 %{buildroot}%{_datadir}/%{pkg_name}-%{version}/msv
cp -pr msv/examples/* %{buildroot}%{_datadir}/%{pkg_name}-%{version}/msv
install -d -m 755 %{buildroot}%{_datadir}/%{pkg_name}-%{version}/xsdlib
cp -pr xsdlib/examples/* %{buildroot}%{_datadir}/%{pkg_name}-%{version}/xsdlib

%{?scl:EOF}

%files msv -f .mfiles-msv-msv
%{_javadir}/%{pkg_name}
%dir %{_mavenpomdir}/%{pkg_name}
%doc License.txt
%doc msv/doc/Apache-LICENSE-1.1.txt
%doc Apache-LICENSE-2.0.txt

%files rngconv -f .mfiles-msv-rngconv
%doc msv/doc/Apache-LICENSE-1.1.txt
%doc License.txt

%files xmlgen -f .mfiles-msv-xmlgen
%doc msv/doc/Apache-LICENSE-1.1.txt
%doc License.txt

%files xsdlib -f .mfiles-msv-xsdlib
%doc msv/doc/Apache-LICENSE-1.1.txt
%doc License.txt

%files javadoc -f .mfiles-javadoc
%doc License.txt
%doc msv/doc/Apache-LICENSE-1.1.txt
%doc Apache-LICENSE-2.0.txt

%files manual
%doc %{_docdir}/%{pkg_name}-%{version}
%doc License.txt

%files demo
%{_datadir}/%{pkg_name}-%{version}

%changelog
* Wed Jan 14 2015 Michal Srb <msrb@redhat.com> - 1:2013.5.1-6.16
- Fix directory ownership

* Wed Jan 14 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 1:2013.5.1-6.15
- Add requires on SCL filesystem package

* Tue Jan 13 2015 Michael Simacek <msimacek@redhat.com> - 1:2013.5.1-6.14
- Mass rebuild 2015-01-13

* Mon Jan 12 2015 Michael Simacek <msimacek@redhat.com> - 1:2013.5.1-6.13
- Rebuild to regenerate requires

* Fri Jan 09 2015 Michal Srb <msrb@redhat.com> - 1:2013.5.1-6.12
- Mass rebuild 2015-01-09

* Wed Jan 07 2015 Michal Srb <msrb@redhat.com> - 1:2013.5.1-6.11
- Migrate to .mfiles

* Tue Dec 16 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1:2013.5.1-6.10
- Migrate requires and build-requires to rh-java-common

* Mon Dec 15 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1:2013.5.1-6.9
- Mass rebuild 2014-12-15

* Mon Dec 15 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1:2013.5.1-6.8
- Rebuild for rh-java-common collection

* Mon May 26 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1:2013.5.1-6.7
- Mass rebuild 2014-05-26

* Wed Feb 19 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1:2013.5.1-6.6
- Mass rebuild 2014-02-19

* Tue Feb 18 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1:2013.5.1-6.5
- Mass rebuild 2014-02-18

* Tue Feb 18 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1:2013.5.1-6.4
- Remove requires on java

* Mon Feb 17 2014 Michal Srb <msrb@redhat.com> - 1:2013.5.1-6.3
- SCL-ize BR/R

* Thu Feb 13 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1:2013.5.1-6.2
- Rebuild to regenerate auto-requires

* Tue Feb 11 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 1:2013.5.1-6.1
- First maven30 software collection build

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 1:2013.5.1-6
- Mass rebuild 2013-12-27

* Tue Aug 27 2013 Michal Srb <msrb@redhat.com> - 1:2013.5.1-5
- Migrate away from mvn-rpmbuild (Resolves: #997443)

* Thu Aug 01 2013 Michal Srb <msrb@redhat.com> - 1:2013.5.1-4
- Fix license tag (+Public Domain)
- Add create-tarball.sh to SRPM

* Wed Jul 31 2013 Michal Srb <msrb@redhat.com> - 1:2013.5.1-3
- Do not build module with unclear licensing (relames)
- Replace %%add_to_maven_depmap with %%add_maven_depmap

* Fri Jun 28 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1:2013.5.1-2
- Rebuild to regenerate API documentation
- Resolves: CVE-2013-1571

* Fri Jun 07 2013 Michal Srb <msrb@redhat.com> - 1:2013.5.1-1
- Update to latest upstream version 2013.5.1
- Clean up tarball
- Fix BR/R

* Fri Apr 12 2013 Michal Srb <msrb@redhat.com> - 1:2013.2.3-3
- Fix license tags in javadoc, manual, demo subpackages

* Fri Apr 12 2013 Michal Srb <msrb@redhat.com> - 1:2013.2.3-2
- Fix license tag for msv subpackage
- Remove unneeded patches

* Thu Apr 11 2013 Michal Srb <msrb@redhat.com> - 1:2013.2.3-1
- Update to upstream version 2013.2.3
- Resolves: rhbz#876845
- Fix URL and license tag

* Mon Feb 25 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 1:2009.1-14
- Add missing BR: maven-local

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:2009.1-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:2009.1-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Apr 6 2012 Alexander Kurtakov <akurtako@redhat.com> 1:2009.1-11
- Drop unneeded BR/R.

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:2009.1-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Nov 29 2011 Alexander Kurtakov <akurtako@redhat.com> 1:2009.1-9
- Build with maven 3.
- Adapt to current guidelines.

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:2009.1-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Nov  2 2010 Ville Skyttä <ville.skytta@iki.fi> - 1:2009.1-7
- Add msv, relames, xmlgen, and rngconv command line scripts.

* Thu Oct 28 2010 Alexander Kurtakov <akurtako@redhat.com> 1:2009.1-6
- BR junit4.

* Thu Oct 28 2010 Alexander Kurtakov <akurtako@redhat.com> 1:2009.1-5
- Fix depmaps and install jars required by msv.pom.

* Fri Sep 24 2010 Mat Booth <fedora@matbooth.co.uk> - 1:2009.1-4
- Really require a version of xml-commons-resolver that provides the necessary
  maven pom and depmap.

* Sun Sep 19 2010 Mat Booth <fedora@matbooth.co.uk> - 1:2009.1-3
- Require a version of xml-commons-resolver that provides the necessary maven
  pom and depmap.

* Sun Sep 19 2010 Mat Booth <fedora@matbooth.co.uk> - 1:2009.1-2
- Re-patch build to link to local javadocs.
- Install maven poms/depmap.

* Thu Sep 16 2010 Mat Booth <fedora@matbooth.co.uk> - 1:2009.1-1
- Update to latest tagged release.
- Drop support for GCJ ahead of time compilation.
- Fix RHBZ #627688, RHBZ #631076
- This project now builds with maven instead of ant.
- The new build in this release aggregates javadocs, so now we have one javadoc
  package that obsoletes the many javadoc packages we had before.
- Use new jar names that upstream use, provide the old names.
- Misc other changes for guideline compliance.

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.2-0.4.20050722.3.4.1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Fri May 08 2009 Karsten Hopp <karsten@redhat.com> 1.2-0.3.20050722.3.4.1
- Specify source and target as 1.4 to make it build

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1:1.2-0.3.20050722.3.4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Jul  9 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 1:1.2-0.2.20050722.3.4
- drop repotag

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 1:1.2-0.2.20050722.3jpp.3
- Autorebuild for GCC 4.3

* Wed Sep 12 2007 Matt Wringe <mwringe@redhat.com> 0:1,2-0.1.20050722.3jpp.3
- Make package build with new gcj. Remove .class files from demo package and
  remove demo exclude from aot-compile-rpm 

* Tue Sep 11 2007 Matt Wringe <mwringe@redhat.com> 0:1.2-0.1.20050722.3jpp.2
- Fix unowned directories
- Change copyright files to utf-8 format
- Change license field to BSD (from BSD-Style)

* Fri Feb 16 2007 Andrew Overholt <overholt@redhat.com> 0:1.2-0.1.20050722.3jpp.1
- Remove postun Requires on jpackage-utils
- Set gcj_support to 1
- Fix groups to shut up rpmlint
- Add versions to the Provides and Obsoletes
- Add patch to take out Class-Path in MANIFEST.MF

* Thu Feb 15 2007 Matt Wringe <mwringe at redhat.com> - 0:1.2-0.1.20050722.3jpp.1.fc7
- Extract sources from a fresh CVS export of the given tag and add extra source
  required to build the package not present in the 20050722 tag anymore
- Add a patch to remove compile time dependency on crimson
- Add a patch to enable compression of jar files
- Add jpackage-utils as a requires for the packages/subpackages

* Mon Feb 12 2007 Ralph Apel <r.apel at r-apel.de> - 0:1.2-0.20050722.3jpp
- Add bootstrap option to build without saxon nor jdom
- Add gcj_support option

* Mon Feb 17 2006 Fernando Nasser <fnasser@redhat.com> - 0:1.2-0.20050722.2jpp
- First JPP 1.7 build

* Wed Aug 17 2005 Ralph Apel <r.apel at r-apel.de> - 0:1.2-0.20050722.1jpp
- First JPP from this code base
