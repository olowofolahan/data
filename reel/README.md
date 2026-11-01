# Christmas tree reel: editable project

The final MP4 isn't stored in git because it's over GitHub's 100 MB limit and contains family footage. It's delivered separately.

- `deliver/EDIT_DECISION_LIST.md`: shot-by-shot list (reel time, source clip, in/out, story beat, mask method)
- `deliver/christmas_reel.edl`: CMX3600 EDL; import it into Premiere, Resolve or Final Cut and relink to the original WhatsApp files
- `deliver/cover.jpg`: cover frame (no children visible)
- `tools/edl.py`: the edit itself (shots, dissolves, text). Change it and re-render.
- `tools/make_tracks.py` + `edit/tracks.json`: child-face mask tracks (source-pixel keyframes)
- `tools/render.py`: grade, 1080x1920 upscale, Santa-sticker masking, dissolves, text
- `tools/music.py`: original synthesized "Deck the Halls" (traditional, public domain) at 96 BPM
- `tools/mix.py`: music, natural sound and ducking. Loudness is then normalized to -14 LUFS with ffmpeg loudnorm.

To re-render, put the clips in `raw/` as v17/v19/v20/v21.mp4, then run
`python3 tools/make_tracks.py && python3 tools/music.py && python3 tools/render.py && python3 tools/mix.py`
and mux the result with ffmpeg (see the commands in the session log).
