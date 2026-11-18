# CI/CD Pipeline Examples

Pin images and tool versions so the same commit builds the same way next year.

## GitLab CI – build, test, quality, site, release

```yaml
image: maven:3.9-eclipse-temurin-21-alpine

variables:
  MAVEN_OPTS: "-Dmaven.repo.local=.m2/repository"

cache:
  paths:
    - .m2/repository

stages:
  - build
  - test
  - deploy
  - release

build:
  stage: build
  script:
    - mvn -B compile

verify:
  stage: test
  script:
    - mvn -B verify               # tests + checkstyle + pmd/cpd + jacoco gate
  artifacts:
    when: always
    reports:
      junit: target/surefire-reports/TEST-*.xml
    paths:
      - target/site/jacoco/

pages:                            # publish the project site (docs, reports)
  stage: deploy
  script:
    - mvn -B site
    - mv target/site public
  artifacts:
    paths: [public]
  rules:
    - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

release:                          # only on version tags
  stage: release
  rules:
    - if: $CI_COMMIT_TAG =~ /^v\d+\.\d+\.\d+$/
  variables:
    JRELEASER_GITLAB_TOKEN: $RELEASE_TOKEN   # masked + protected CI variable
  script:
    - mvn -B package -DskipTests             # tests ran in the test stage
    - mvn -B jreleaser:full-release
  artifacts:
    paths: [out/jreleaser/]
```

Merge requests show pipeline status and test reports; configure "pipelines must
succeed" before merge.

## GitHub Actions – equivalent

```yaml
name: ci
on:
  push:
    branches: [main]
  pull_request:

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '21'
          cache: maven
      - run: ./mvnw -B verify
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: reports
          path: |
            target/surefire-reports
            target/site/jacoco
```

Node/TypeScript equivalent steps: `npm ci`, `npm run lint`, `npm test -- --coverage`,
`npm run build`. Python: `uv sync`, `uv run ruff check`, `uv run pytest --cov`.

## Release with jReleaser (Java)

`jreleaser.yml` in the project root:

```yaml
project:
  name: my-app
  description: Short description
  license: Apache-2.0
  java:
    groupId: com.example
    version: 21
release:
  gitlab:                      # or github:
    host: https://gitlab.example.com
    apiEndpoint: https://gitlab.example.com/api/v4
    projectIdentifier: 12345678
    changelog:
      formatted: ALWAYS
      preset: conventional-commits   # release notes from commit messages
distributions:
  my-app:
    type: SINGLE_JAR
    artifacts:
      - path: target/my-app-{{projectVersion}}.jar
```

Declare `org.jreleaser:jreleaser-maven-plugin` in the POM. Release ritual:

```bash
git tag -a v1.0.1 -m "Release 1.0.1"
git push origin v1.0.1
```

For end users without a JDK, a native-installer tool (e.g. jDeploy, jpackage) may
fit better; for libraries, publish to a package registry.

## Comparing metrics before merge (agentic or CI)

1. Run the build with reports on the target branch (or use stored CI reports) and
   on the feature branch.
2. Compare: coverage (branch, per class), number of static analysis violations,
   duplication, max/avg CC, class fan-out / package dependencies.
3. Any regression → fix before merge, or create an issue describing the deviation
   and its impact and ask the user/team whether to fix it now.

## Security in pipelines

- Use masked, protected variables or job tokens; never personal tokens; never
  echo secrets.
- Add dependency vulnerability scanning and secret scanning (e.g. gitleaks).
