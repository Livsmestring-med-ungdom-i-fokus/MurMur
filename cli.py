"""
CLI Interface for Music AI Studio

Command-line interface for interactive music production.
"""

import argparse
import sys
import json
from pathlib import Path

from music_ai_studio import MusicAIStudio


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
    
    args = parser.parse_args()
    
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
        "quit": "Exit"
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
            
            print(f"❌ Unknown command: {user_input}")
        
        except KeyboardInterrupt:
            print("\n\nGoodbye! 🎶")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
