---
name: logging
description: Logging done deliberately. Use when adding, reviewing or configuring logs, replacing print/console statements with a logging framework, choosing log levels, logging exceptions, designing audit logs, or writing a logging concept (Log4j2, Logback, SLF4J, java.util.logging, Python logging, winston/pino).
---

# Logging

A log is the written trace a running system leaves: what it decided to do, with
what inputs, in what order. It is the only way to investigate failures that can't
be reproduced on a developer machine (production, load, timing, distributed
systems, events hours after the trigger).

## Two kinds of logs – keep them apart

- **Technical (debug) logs** – for developers diagnosing problems: errors, state,
  control flow. Verbose in development, quiet in production.
- **Audit logs** – what users/the system did (who, what, which object, when) for
  operations, security, compliance. Different readers, retention and often storage;
  use a separate logger hierarchy (e.g. `audit.payments`) with its own appender and
  `additivity="false"` so entries don't also land in the technical log.

## Use a framework, never print statements

`System.out.println` / `print` / `console.log` can't be filtered by level or
module, redirected, formatted or reconfigured without code changes. A framework
separates *what might be logged* (in code) from *whether, where and how* (in
configuration). Prefer a facade (SLF4J in Java) in libraries.

Concepts: **level** (statement severity and logger threshold), **logger** (named,
hierarchical – name it after the class), **appender** (destination: console, file,
rolling file, syslog…), **layout** (format).

```java
private static final Logger logger = LogManager.getLogger(RentalService.class);
```

## Levels

| Level | Use for |
|---|---|
| FATAL | the application cannot continue (rarely useful in practice) |
| ERROR | an operation failed; the app continues (e.g. no DB connection, payment failed after retries) |
| WARN | harmful or unexpected but handled; needs attention in the medium term |
| INFO | coarse progress and state changes: start/stop, completed jobs (sparingly) |
| DEBUG | diagnostic state at meaningful points (development) |
| TRACE | fine-grained control flow (development, constant strings only) |

Production typically runs at INFO or WARN. Expected, normal events (invalid user
input that the UI handles) are not logged as problems.

## Writing useful messages

- A message must make sense on its own line, read months later without the code:
  operation + intent + relevant data.
  - Bad: `logger.debug(anId);`
  - Good: `logger.debug("setId called with id={}", anId);`
- Use parameterised messages (`{}` placeholders) – nothing is built when the level
  is disabled. Guard blocks that compute data only for logging with
  `if (logger.isDebugEnabled())`; use lambdas/suppliers for one expensive argument.
- English for technical logs; consistent wording.
- **Never log secrets or personal data**: passwords, tokens, session IDs, full card
  numbers, personal identifiers. Logs end up in backups, aggregators and screens.

## Exceptions

- Log with the exception object attached: `logger.error("Order {} could not be
  loaded", orderId, ex)` – never `printStackTrace()`.
- Log the failure **once, where it is handled** (where you decide: retry, fall
  back, report, abort). Not at every layer.
- When translating a technical exception into a domain exception, keep the cause
  (`new OrderLookupException("...", ex)`); add a WARN at the catch site only if it
  adds context the caller won't have (IDs, attempts).
- Log what the program was doing, not just the exception text.
- Never swallow exceptions silently.

## Cost

Disabled statements cost a call and a comparison; enabled ones cost formatting and
I/O (synchronous file writes: tens of µs; async appenders: ~1 µs). Location
patterns (`%l`, `%L`, `%M`) are expensive – use them only for rare entries.
Argument evaluation happens even for disabled statements unless you use
placeholders/guards/lambdas.

## Configuration (Log4j2 example)

```xml
<Configuration>
  <Appenders>
    <Console name="console" target="SYSTEM_OUT">
      <PatternLayout pattern="%d [%t] %-5p %c - %m%n"/>
    </Console>
    <RollingFile name="file" fileName="logs/app.log"
                 filePattern="logs/app.%d{yyyy-MM-dd}.log">
      <PatternLayout pattern="%d [%t] %-5p %c - %m%n"/>
      <Policies><TimeBasedTriggeringPolicy/></Policies>
    </RollingFile>
    <RollingFile name="auditFile" fileName="logs/audit.log"
                 filePattern="logs/audit.%d{yyyy-ww}.log">
      <PatternLayout pattern="%d %c{2}+%m%n"/>
      <Policies><TimeBasedTriggeringPolicy/></Policies>
    </RollingFile>
  </Appenders>
  <Loggers>
    <Logger name="com.example.rental" level="debug"/>
    <Logger name="audit" level="info" additivity="false">
      <AppenderRef ref="auditFile"/>
    </Logger>
    <Root level="info">
      <AppenderRef ref="console"/>
      <AppenderRef ref="file"/>
    </Root>
  </Loggers>
</Configuration>
```

Place it at `src/main/resources/log4j2.xml`. Production: rolling files (or stdout
collected by the platform), not an unbounded single file.

## Logging concept

On real projects write the decisions down once (in the docs): goals of logging,
logger naming (class-based technical, purpose-based audit), level usage rules,
appenders per environment, layouts, what must never be logged, coding style
(exceptions only in catch, always with the exception object, at least WARN; audit
entries at the end of a service method when success is known). Then apply it
consistently.

## Tests

Don't assert on log output for business behaviour; if logging is a requirement
(audit), inject the audit logger/port and verify it like any other collaborator.
