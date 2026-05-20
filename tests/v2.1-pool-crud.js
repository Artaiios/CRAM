/* V2.1 Pool-CRUD Tests — TODO: hook up to a test runner.
 *
 * These cases document the contract of the Storage-layer pool helpers and
 * the orphan-/cleanup-logic in handleDeleteRole / handleDeletePerson. They
 * are not wired to a runner yet; the existing repo test surface (Playwright
 * pen-test only) does not cover Storage. Once a unit-test harness lands,
 * each numbered case becomes one it()/test() block.
 *
 * Setup precondition for every case: a State.config with v3 schema
 * (schemaVersion=3, pools=[], every person has keywords=[]). Use
 * Storage.migrateConfigV3 on a fixture if you build from a v1 dump.
 *
 * --- Pool CRUD --------------------------------------------------------
 *
 *   T1  addPool({ name: 'IT-Sec' }) returns a pool with:
 *         - id matching /^pool-/
 *         - name === 'IT-Sec'
 *         - leadRoleId === null
 *         - memberIds === []
 *         - notes === ''
 *         - secondaryLeadRoleIds === []
 *       and pushes the pool onto State.config.pools.
 *
 *   T2  removePool(id) removes the matching entry, returns true.
 *       removePool('nonexistent') returns false, leaves pools unchanged.
 *
 *   T3  updatePool(id, { notes: 'foo' }) patches notes only; name,
 *       leadRoleId, memberIds untouched.
 *       updatePool(id, { leadRoleId: '<nonexistent-role>' }) throws.
 *       updatePool(id, { leadRoleId: null }) clears the lead slot.
 *       updatePool(id, { name: '   ' }) throws (empty after trim).
 *
 *   T4  addPoolMember(poolId, personId) is idempotent: calling twice
 *       leaves exactly one entry in pool.memberIds.
 *
 *   T5  removePoolMember(poolId, personId) returns false silently if the
 *       person was never a member; returns true and persists if they were.
 *
 * --- Keyword helpers --------------------------------------------------
 *
 *   T6  setPersonKeywords(p1, ['  itsec ', 'ITSec', '', 'SOC'])
 *         → person.keywords === ['itsec', 'SOC']   (trimmed, deduped
 *           case-insensitively, first-seen original case preserved,
 *           empties dropped).
 *
 *   T7  getAllKeywords() returns a locale-sorted, case-insensitively
 *       deduped union across all persons. Pure read — no markDirty,
 *       no localStorage write.
 *
 * --- Orphan-/cleanup-logic --------------------------------------------
 *
 *   T8  handleDeleteRole(roleId) where pool.leadRoleId === roleId:
 *         → pool.leadRoleId becomes null, pool is NOT removed.
 *
 *   T9  handleDeleteRole(roleId) where pool.secondaryLeadRoleIds
 *       contains roleId:
 *         → roleId is filtered out of secondaryLeadRoleIds.
 *       Members are NOT touched in either case.
 *
 *  T10  handleDeletePerson(personId) where personId is in two pools'
 *       memberIds:
 *         → both pools have personId filtered out of memberIds.
 *         → State.config.persons no longer contains the person.
 *
 * --- Migration coverage on import paths -------------------------------
 *
 *  T11  Each of the four import sites pipes the incoming config
 *       through Storage.migrateConfigV3 before assigning to
 *       State.config:
 *         - Sync.applyEnvelope               (plain envelope)
 *         - Sync.applyEnvelopeForSource     (per-source, encrypted+plain)
 *         - qrApplyReceivedPayload          (QR import path)
 *         - applyImport                     (JSON file import path)
 *       Feed each one a v1-shaped config (no pools, persons without
 *       keywords) and assert State.config.pools is [] and every person
 *       has a keywords array after apply.
 *
 *  T12  migrateConfigV3 is defensive: passing null, undefined, {}, or
 *       'string' must not throw and must return the input unchanged
 *       (no upgrade attempted on non-objects).
 */
