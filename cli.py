"""
CLI Interface for Music AI Studio

Command-line interface for interactive music production.
"""

import argparse
import sys
import json
from pathlib import Path

from music_ai_studio import MusicAIStudio
from music_ai_core.learning import list_lessons, list_exercise_types
from music_ai_core.dance import list_genres, genre_description
from music_ai_core.artist_mode import list_styles
from music_ai_core.elements import list_scales, list_chords, list_rhythms


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Music AI Studio - Modular AI Music Production",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  %(prog)s --interactive
  
  # Generate music from prompt
  %(prog)s --prompt "upbeat electronic dance track"
  
  # With ChatGPT integration
  %(prog)s --interactive --chatgpt
  
  # Show system info
  %(prog)s --info
        """
    )
    
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Start interactive mode"
    )
    
    parser.add_argument(
        "-p", "--prompt",
        type=str,
        help="Music generation prompt"
    )
    
    parser.add_argument(
        "-c", "--chatgpt",
        action="store_true",
        help="Enable ChatGPT integration"
    )
    
    parser.add_argument(
        "--tempo",
        type=int,
        default=120,
        help="Set studio tempo (default: 120)"
    )
    
    parser.add_argument(
        "--sample-rate",
        type=int,
        default=44100,
        help="Audio sample rate (default: 44100)"
    )
    
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show system information"
    )
    
    parser.add_argument(
        "--example",
        type=int,
        help="Run example (1-5)"
    )

    parser.add_argument(
        "--elements",
        action="store_true",
        help="Show available scales, chords, and rhythms"
    )

    parser.add_argument(
        "--dance",
        type=str,
        metavar="GENRE",
        help="Generate a drum beat for GENRE (e.g. house, techno, hip_hop). "
             "Use 'list' to show available genres."
    )

    parser.add_argument(
        "--dance-bpm",
        type=int,
        default=None,
        help="BPM override for --dance (default: genre default)"
    )

    parser.add_argument(
        "--dance-bars",
        type=int,
        default=4,
        help="Number of bars for --dance (default: 4)"
    )

    parser.add_argument(
        "--artist",
        type=str,
        metavar="STYLE",
        help="Build a song arrangement for STYLE (e.g. pop, edm, jazz). "
             "Use 'list' to show available styles."
    )

    parser.add_argument(
        "--artist-title",
        type=str,
        default="Untitled",
        help="Song title for --artist arrangement (default: 'Untitled')"
    )

    parser.add_argument(
        "--artist-key",
        type=str,
        default=None,
        help="Key for --artist arrangement (e.g. C, D#)"
    )

    parser.add_argument(
        "--artist-bpm",
        type=int,
        default=None,
        help="BPM override for --artist arrangement"
    )

    parser.add_argument(
        "--lesson",
        type=str,
        metavar="LESSON_ID",
        help="Start a music theory lesson (e.g. el_01). "
             "Use 'list' to show all lessons."
    )

    parser.add_argument(
        "--exercise",
        type=str,
        metavar="TYPE",
        help="Run a practice exercise (e.g. scale_building, chord_building). "
             "Use 'list' to see all exercise types."
    )

    parser.add_argument(
        "--exercise-difficulty",
        type=str,
        default="beginner",
        choices=["beginner", "intermediate", "advanced"],
        help="Difficulty for --exercise (default: beginner)"
    )

    parser.add_argument(
        "--inspiration",
        action="store_true",
        help="Print a random creative inspiration prompt"
    )
    
    args = parser.parse_args()
    
    # ------------------------------------------------------------------
    # Lightweight commands that don't need the studio to be fully started
    # ------------------------------------------------------------------

    if args.elements:
        print("\n🎵 Elements – available scales:")
        for s in list_scales():
            print(f"   {s}")
        print("\n🎵 Elements – available chord types:")
        for c in list_chords():
            print(f"   {c}")
        print("\n🎵 Elements – available rhythm patterns:")
        for r in list_rhythms():
            print(f"   {r}")
        return

    if args.dance == "list":
        print("\n🥁 Available dance genres:")
        for g in list_genres():
            print(f"   {genre_description(g)}")
        return

    if args.artist == "list":
        print("\n🎸 Available artist styles:", ", ".join(list_styles()))
        return

    if args.lesson == "list":
        print("\n📖 Available lessons:")
        from music_ai_core.learning import LESSONS
        for lid in list_lessons():
            lesson = LESSONS[lid]
            print(f"   {lid:6s} | {lesson.track:8s} | {lesson.difficulty:14s} | {lesson.title}")
        return

    if args.exercise == "list":
        print("\n🎯 Available exercise types:", ", ".join(list_exercise_types()))
        return

    # ------------------------------------------------------------------
    # Full studio commands
    # ------------------------------------------------------------------

    # Initialize studio
    studio = MusicAIStudio(use_chatgpt=args.chatgpt, sample_rate=args.sample_rate)
    
    # Show system info
    if args.info:
        info = studio.orchestrator.get_system_info()
        print("\n🎛️  System Information:")
        print(json.dumps(info, indent=2))
        return
    
    # Process prompt
    if args.prompt:
        studio.set_studio_tempo(args.tempo)
        result = studio.get_music_prompt(args.prompt)
        print("\n📊 Result:")
        print(json.dumps(result, indent=2, default=str))
        return
    
    # Run example
    if args.example:
        from examples import (
            example_basic_workflow,
            example_effects_processing,
            example_composition_creation,
            example_module_orchestration,
            example_with_chatgpt_direction
        )
        
        examples = {
            1: example_basic_workflow,
            2: example_with_chatgpt_direction,
            3: example_effects_processing,
            4: example_composition_creation,
            5: example_module_orchestration,
        }
        
        if args.example in examples:
            examples[args.example]()
        else:
            print(f"Example {args.example} not found. Available: 1-5")
        return

    # Dance beat generation
    if args.dance:
        studio.generate_beat(
            genre=args.dance,
            bpm=args.dance_bpm,
            bars=args.dance_bars,
        )
        mixed = studio.studio.mix()
        if mixed.size:
            print(f"✓ Mixed beat: {mixed.shape[1]} samples "
                  f"({mixed.shape[1] / studio.sample_rate:.2f}s)")
        return

    # Artist arrangement
    if args.artist:
        result = studio.build_arrangement(
            title=args.artist_title,
            style=args.artist,
            key=args.artist_key,
            bpm=args.artist_bpm,
        )
        print("\n📋 Arrangement JSON:")
        print(json.dumps(result, indent=2, default=str))
        return

    # Inspiration
    if args.inspiration:
        studio.get_inspiration()
        return

    # Lesson
    if args.lesson:
        studio.start_lesson(args.lesson)
        return

    # Exercise
    if args.exercise:
        studio.practice_exercise(args.exercise, args.exercise_difficulty)
        return
    
    # Interactive mode
    if args.interactive:
        interactive_mode(studio)
        return
    
    # Default: show help
    parser.print_help()


def interactive_mode(studio: MusicAIStudio):
    """Interactive CLI mode."""
    print("\n" + "=" * 60)
    print("🎵 Music AI Studio - Interactive Mode")
    print("=" * 60)
    print("Type 'help' for available commands, 'quit' to exit")
    print("=" * 60 + "\n")
    
    commands = {
        "help": "Show available commands",
        "status": "Show studio status",
        "tempo <bpm>": "Set tempo",
        "generate <track> <notes>": "Generate track (e.g., 'generate track_0 C D E F')",
        "effect <track> <type> <params>": "Add effect (reverb/delay/compression)",
        "mix": "Mix and show result",
        "prompt <text>": "Process music prompt",
        # new module commands
        "scale <root> [type] [octave]": "Show notes of a scale (e.g. 'scale C major 4')",
        "chord <root> [type] [octave]": "Show notes of a chord (e.g. 'chord A minor 4')",
        "melody <track> <root> [type]": "Generate a scale melody to a track",
        "beat <genre> [bpm] [bars]": "Generate a drum beat (e.g. 'beat house 125 4')",
        "arrange <style> [title]": "Build a song arrangement (e.g. 'arrange pop MySong')",
        "inspire": "Get a random creative inspiration",
        "lesson <id>": "Start a lesson (e.g. 'lesson el_01'; 'lesson list')",
        "exercise <type>": "Run a practice exercise (e.g. 'exercise scale_building')",
        "score": "Show your learning score",
        "quit": "Exit",
    }
    
    while True:
        try:
            user_input = input("\n🎛️  > ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == "quit":
                print("Goodbye! 🎶")
                break
            
            if user_input.lower() == "help":
                print("\nAvailable commands:")
                for cmd, desc in commands.items():
                    print(f"  {cmd:30s} - {desc}")
                continue
            
            if user_input.lower() == "status":
                state = studio.get_studio_state()
                print(f"\nTempo: {state['tempo']} BPM")
                print(f"Tracks: {state['num_tracks']}")
                continue
            
            if user_input.lower().startswith("tempo"):
                parts = user_input.split()
                if len(parts) > 1:
                    try:
                        bpm = int(parts[1])
                        studio.set_studio_tempo(bpm)
                        print(f"✓ Tempo set to {bpm} BPM")
                    except ValueError:
                        print("❌ Invalid tempo value")
                continue
            
            if user_input.lower().startswith("generate"):
                parts = user_input.split(maxsplit=2)
                if len(parts) >= 3:
                    track = parts[1]
                    notes = parts[2]
                    studio.generate_track(track, notes)
                    print(f"✓ Generated {track}")
                continue
            
            if user_input.lower().startswith("mix"):
                mixed = studio.studio.mix()
                print(f"✓ Mixed: {mixed.shape} stereo samples")
                print(f"  Duration: {mixed.shape[1] / studio.sample_rate:.2f}s")
                continue
            
            if user_input.lower().startswith("prompt"):
                prompt = user_input[6:].strip()
                result = studio.get_music_prompt(prompt)
                if "interpretation" in result.get("stages", {}):
                    interp = result["stages"]["interpretation"]
                    print(f"✓ Interpretation:")
                    print(f"  Genre: {interp.get('genre')}")
                    print(f"  Tempo: {interp.get('tempo')}")
                continue

            # ----------------------------------------------------------
            # Elements commands
            # ----------------------------------------------------------

            if user_input.lower().startswith("scale"):
                parts = user_input.split()
                root = parts[1] if len(parts) > 1 else "C"
                scale_type = parts[2] if len(parts) > 2 else "major"
                octave = int(parts[3]) if len(parts) > 3 else 4
                try:
                    notes = studio.get_scale(root, scale_type, octave)
                    note_names = " ".join(k.rstrip("01234567890") for k, _ in notes)
                    print(f"✓ {root} {scale_type}: {note_names}")
                except ValueError as e:
                    print(f"❌ {e}")
                continue

            if user_input.lower().startswith("chord"):
                parts = user_input.split()
                root = parts[1] if len(parts) > 1 else "C"
                chord_type = parts[2] if len(parts) > 2 else "major"
                octave = int(parts[3]) if len(parts) > 3 else 4
                try:
                    notes = studio.get_chord(root, chord_type, octave)
                    note_names = " ".join(k.rstrip("01234567890") for k, _ in notes)
                    print(f"✓ {root} {chord_type}: {note_names}")
                except ValueError as e:
                    print(f"❌ {e}")
                continue

            if user_input.lower().startswith("melody"):
                parts = user_input.split()
                if len(parts) >= 3:
                    track = parts[1]
                    root = parts[2]
                    scale_type = parts[3] if len(parts) > 3 else "major"
                    studio.generate_scale_melody(track, root, scale_type)
                else:
                    print("Usage: melody <track_name> <root> [scale_type]")
                continue

            # ----------------------------------------------------------
            # Dance command
            # ----------------------------------------------------------

            if user_input.lower().startswith("beat"):
                parts = user_input.split()
                genre = parts[1] if len(parts) > 1 else "house"
                bpm = int(parts[2]) if len(parts) > 2 else None
                bars = int(parts[3]) if len(parts) > 3 else 4
                try:
                    studio.generate_beat(genre=genre, bpm=bpm, bars=bars)
                except ValueError as e:
                    print(f"❌ {e}")
                continue

            # ----------------------------------------------------------
            # Artist mode commands
            # ----------------------------------------------------------

            if user_input.lower().startswith("arrange"):
                parts = user_input.split(maxsplit=2)
                style = parts[1] if len(parts) > 1 else "pop"
                title = parts[2] if len(parts) > 2 else "Untitled"
                try:
                    studio.build_arrangement(title=title, style=style)
                except ValueError as e:
                    print(f"❌ {e}")
                continue

            if user_input.lower().strip() == "inspire":
                studio.get_inspiration()
                continue

            # ----------------------------------------------------------
            # Learning commands
            # ----------------------------------------------------------

            if user_input.lower().startswith("lesson"):
                parts = user_input.split()
                lesson_id = parts[1] if len(parts) > 1 else "list"
                if lesson_id == "list":
                    from music_ai_core.learning import LESSONS, list_lessons
                    print("\n📖 Available lessons:")
                    for lid in list_lessons():
                        lesson = LESSONS[lid]
                        print(f"   {lid:6s} | {lesson.track:8s} | "
                              f"{lesson.difficulty:14s} | {lesson.title}")
                else:
                    try:
                        studio.start_lesson(lesson_id)
                    except ValueError as e:
                        print(f"❌ {e}")
                continue

            if user_input.lower().startswith("exercise"):
                parts = user_input.split()
                ex_type = parts[1] if len(parts) > 1 else "note_identification"
                difficulty = parts[2] if len(parts) > 2 else "beginner"
                if ex_type == "list":
                    from music_ai_core.learning import list_exercise_types
                    print("Available exercise types:", ", ".join(list_exercise_types()))
                else:
                    try:
                        studio.practice_exercise(ex_type, difficulty)
                    except Exception as e:
                        print(f"❌ {e}")
                continue

            if user_input.lower().strip() == "score":
                studio.get_learning_score()
                continue
            
            print(f"❌ Unknown command: {user_input}")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye! 🎶")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
