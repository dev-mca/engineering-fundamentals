# Maven Reference: Lifecycle, Project Layout and a Quality Gate

Check Maven Central for current plugin versions before copying; versions below
were current in 2026.

## Lifecycle essentials

Three lifecycles: `clean`, `default`, `site`. Running a phase runs every earlier
phase of that lifecycle.

| Phase | Does |
|---|---|
| validate | checks the POM |
| compile | compiles `src/main/java` |
| test | compiles and runs `src/test/java` (Surefire) |
| package | builds the JAR/WAR |
| integration-test | runs integration tests (Failsafe) |
| verify | runs checks on the package – the quality gate phase |
| install | puts the artefact into `~/.m2/repository` |
| deploy | publishes to a remote repository |

Plugins do the work; their goals bind to phases (defaults come from the Super POM;
inspect with `mvn help:effective-pom`). Calling a goal directly
(`mvn surefire:test`) runs only that goal. Several goals in one phase: default
bindings first, then explicit bindings in POM order.

Layout (convention over configuration):

```
pom.xml
src/main/java        src/main/resources
src/test/java        src/test/resources
target/              ← generated, never commit
```

Dependency scopes: `compile` (default, transitive), `provided`, `runtime`,
`test` (test only, not transitive), `system`, `import` (BOMs in
`<dependencyManagement>`). Keep versions in `<properties>`; import BOMs
(e.g. `org.junit:junit-bom`) for families of artefacts. Conflicting transitive
versions: nearest declaration wins – inspect with `mvn dependency:tree` and pin
explicitly when needed.

Configuration in `<build>` is **not** applied to `<reporting>` automatically –
configure report plugins again (share versions via properties).

## Quality gate POM excerpt

```xml
<properties>
  <maven.compiler.release>21</maven.compiler.release>
  <checkstyle.plugin.version>3.6.0</checkstyle.plugin.version>
  <pmd.plugin.version>3.26.0</pmd.plugin.version>
  <jacoco.version>0.8.15</jacoco.version>
</properties>

<build>
  <plugins>
    <!-- Conventions, complexity, coupling -->
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-checkstyle-plugin</artifactId>
      <version>${checkstyle.plugin.version}</version>
      <configuration>
        <configLocation>checkstyle.xml</configLocation>
        <consoleOutput>true</consoleOutput>
        <failOnViolation>true</failOnViolation>   <!-- this makes it a gate -->
      </configuration>
      <executions>
        <execution>
          <id>checkstyle-check</id>
          <phase>verify</phase>
          <goals><goal>check</goal></goals>
        </execution>
      </executions>
    </plugin>

    <!-- Bug patterns + duplication -->
    <plugin>
      <groupId>org.apache.maven.plugins</groupId>
      <artifactId>maven-pmd-plugin</artifactId>
      <version>${pmd.plugin.version}</version>
      <configuration>
        <rulesets>
          <ruleset>/category/java/bestpractices.xml</ruleset>
          <ruleset>/category/java/errorprone.xml</ruleset>
        </rulesets>
        <failOnViolation>true</failOnViolation>
        <minimumTokens>50</minimumTokens>
      </configuration>
      <executions>
        <execution>
          <id>pmd-check</id>
          <phase>verify</phase>
          <goals><goal>check</goal><goal>cpd-check</goal></goals>
        </execution>
      </executions>
    </plugin>

    <!-- Coverage -->
    <plugin>
      <groupId>org.jacoco</groupId>
      <artifactId>jacoco-maven-plugin</artifactId>
      <version>${jacoco.version}</version>
      <executions>
        <execution>
          <id>prepare-agent</id>
          <goals><goal>prepare-agent</goal></goals>
        </execution>
        <execution>
          <id>report</id>
          <phase>verify</phase>
          <goals><goal>report</goal></goals>
        </execution>
        <execution>
          <id>check</id>
          <goals><goal>check</goal></goals>
          <configuration>
            <rules>
              <rule>
                <element>CLASS</element>   <!-- stricter than BUNDLE averaging -->
                <limits>
                  <limit>
                    <counter>BRANCH</counter>
                    <value>COVEREDRATIO</value>
                    <minimum>0.70</minimum>
                  </limit>
                </limits>
              </rule>
            </rules>
            <excludes><exclude>**/generated/**</exclude></excludes>
          </configuration>
        </execution>
      </executions>
    </plugin>
  </plugins>
</build>
```

PMD categories: `errorprone` and `security` describe defects (good candidates to
fail the build); `design`, `performance` structural/efficiency problems;
`bestpractices`, `codestyle` conventions (often reported and reviewed). Start with
`bestpractices` + `errorprone`.

Checkstyle's `failsOnError` is a different switch – use `failOnViolation` for a
gate.

## checkstyle.xml with metric limits

```xml
<?xml version="1.0"?>
<!DOCTYPE module PUBLIC "-//Checkstyle//DTD Checkstyle Configuration 1.3//EN"
  "https://checkstyle.org/dtds/configuration_1_3.dtd">
<module name="Checker">
  <module name="TreeWalker">
    <module name="CyclomaticComplexity"><property name="max" value="10"/></module>
    <module name="ClassFanOutComplexity"><property name="max" value="20"/></module>
    <module name="ClassDataAbstractionCoupling"><property name="max" value="7"/></module>
    <module name="MethodLength"><property name="max" value="30"/></module>
    <module name="ParameterNumber"><property name="max" value="5"/></module>
    <module name="MagicNumber"/>
  </module>
</module>
```

Use the same `checkstyle.xml` and Checkstyle version in the IDE plugin so the
editor reports what the build will report. The IDE is a convenience; the build is
the authority.

## Enforcing module boundaries (fitness function)

Checkstyle **ImportControl** fails the build when a package imports what it must
not:

```xml
<!-- checkstyle.xml, inside TreeWalker -->
<module name="ImportControl">
  <property name="file" value="${config_loc}/import-control.xml"/>
</module>
```

```xml
<!-- import-control.xml -->
<!DOCTYPE import-control PUBLIC "-//Checkstyle//DTD ImportControl Configuration 1.4//EN"
  "https://checkstyle.org/dtds/import_control_1_4.dtd">
<import-control pkg="ch.example.ecars">
  <allow pkg="java"/>
  <subpackage name="domain">
    <disallow pkg="ch.example.ecars.ui"/>
    <disallow pkg="ch.example.ecars.payment.stripe"/>
  </subpackage>
  <subpackage name="ui">
    <allow pkg="ch.example.ecars.api"/>
    <disallow pkg="ch.example.ecars.persistence"/>
  </subpackage>
</import-control>
```

Alternatives: ArchUnit tests (Java), dependency-cruiser (JS/TS), import-linter
(Python), Java modules (JPMS).

## Javadoc as a gate

```xml
<plugin>
  <groupId>org.apache.maven.plugins</groupId>
  <artifactId>maven-javadoc-plugin</artifactId>
  <version>3.11.2</version>
  <configuration>
    <doclint>all</doclint>
    <failOnWarnings>true</failOnWarnings>   <!-- missing docs fail the build -->
  </configuration>
  <executions>
    <execution><id>attach-javadocs</id><phase>package</phase><goals><goal>jar</goal></goals></execution>
  </executions>
</plugin>
```

Every plugin follows the same four steps: declare it, run its goal, configure it,
bind it to a phase.
