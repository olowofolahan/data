/* ==========================================================================
 * Turf — backend config
 * --------------------------------------------------------------------------
 * For OPEN multiplayer, fill these with YOUR Supabase project's URL and anon
 * (public) key. Both are safe to ship in client code — the anon key is meant
 * to be public and is guarded by the row-level-security policies in
 * turf/supabase/schema.sql. Leave them empty to fall back to the artifact's
 * built-in shared database (owner + contributors only).
 *   window.TURF_CONFIG.supabaseUrl      e.g. "https://abcd1234.supabase.co"
 *   window.TURF_CONFIG.supabaseAnonKey  the long "anon public" JWT
 * ========================================================================== */
window.TURF_CONFIG = {
  supabaseUrl: "",
  supabaseAnonKey: ""
};
