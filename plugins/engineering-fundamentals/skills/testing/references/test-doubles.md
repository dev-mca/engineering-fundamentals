# Test Isolation and Test Doubles

## Why isolate

Collaborators such as databases, HTTP services, payment providers, the file
system, the system clock and LLMs make tests slow, flaky, non-deterministic or
impossible to run. Tightly coupled code (collaborators created inside the class)
makes them impossible to replace.

**Test isolation:** when testing class A, replace its problematic collaborators
with controlled stand-ins. Simplest form, no framework: pass a `Clock` (or the
current time) instead of calling `now()`.

## Sociable vs solitary tests

- **Sociable** – the class runs with real collaborators that are cheap and stable
  (value objects, pure utilities, in-memory lists).
- **Solitary** – every collaborator is replaced by a double.

**Classicist (Detroit) school:** mostly sociable tests, doubles only at the
awkward edges (DB, network, time); state assertions. Easier refactoring; one broken
class can fail many tests.
**Mockist (London) school:** solitary tests throughout; behaviour assertions.
Precise failures, but tests couple to call patterns.

Practical default: real collaborators when cheap, deterministic and I/O-free; a
hand-rolled stub when the test only needs return values; a mocking framework when
behaviour must be verified or return values vary per test.

## Hand-rolled stub

```java
public class SongStub implements Song {
    @Override public String getTitle()    { return "stubbed-title"; }
    @Override public Duration getLength() { return Duration.ofMinutes(3); }
    @Override public void start()         { }
    @Override public boolean isPlaying()  { return false; }
}

@Test
void playList_containsAddedSongs() {
    MusicJukeBox jukebox = new MusicJukeBox();
    jukebox.addSong(new SongStub());
    assertEquals(1, jukebox.getPlayList().size());
}
```

Plain code, explicit, debuggable – but duplicates across tests and becomes awkward
when behaviour must vary per test.

## Mockito (or your language's equivalent)

```java
@Test
void playSong_startsTheSong() {
    // Given
    Song song = mock(Song.class);
    when(song.getTitle()).thenReturn("A");
    MusicJukeBox jukebox = new MusicJukeBox();
    jukebox.addSong(song);

    // When
    jukebox.play("A");

    // Then – behaviour verification
    verify(song).start();
}
```

Other tools: argument matchers (`any()`, `eq()`), `ArgumentCaptor`, `InOrder`,
`doThrow(...)` to force error paths. Equivalents: `unittest.mock`/`pytest-mock`
(Python), Jest/Vitest mocks (JS/TS), Moq/NSubstitute (.NET).

## Testing an external provider (e.g. payments)

1. Define your own port: `interface PaymentGateway { PaymentResult charge(Money amount, CardToken card); }`
2. Business logic (`BookingService.confirm`) depends only on the port; unit-test it
   with a stub/fake gateway: success, declined, timeout, provider error.
3. Write an adapter per provider (`StripeGateway`, `TwintGateway`) implementing the
   port. Test adapters with integration tests against the provider's sandbox or a
   local HTTP stub (WireMock, MockServer, msw) – not on every unit test run.
4. Optionally add contract tests so all adapters satisfy the same expectations.
5. Adding a provider = adding an adapter; core code and its tests stay untouched.

The same pattern applies to LLM calls: treat the model as a collaborator behind an
interface and replace it in unit tests; evaluate the real model separately.

## Design smells that block isolation → refactoring

| Smell | Fix |
|---|---|
| `new` of a service inside the class | Constructor injection |
| Static non-pure calls (`now()`, `random()`, `Files.read...`) | Parameter (`Clock`), or wrap in a small injectable class |
| `Singleton.getInstance()` | Inject the instance |
| Concrete field without injection point | Constructor parameter |
| Legacy code where bigger changes are risky | Extract & override (last resort) |

"Listen to your tests": eight mocks → too many responsibilities; mock chains → Law
of Demeter violation; mock setup longer than the test → interface too broad;
wishing to mock a private/static call → misplaced responsibility.

## Good practice

- Don't mock what you don't own; wrap it.
- Don't mock value objects.
- Many `verify()` calls = test pinned to implementation path; prefer asserting
  results.
- Shape production code so collaborators are replaceable; don't add test-only
  hooks.
- Stubbing (so the code can run) and expectations (what must happen) should be
  clearly separated in the test.
