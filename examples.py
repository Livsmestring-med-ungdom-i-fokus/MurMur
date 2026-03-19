"""
Example: Live Music Production with Modular AI System

Demonstrates:
- ChatGPT integration for creative direction
- Live studio setup and track generation
- Module orchestration
- Real-time effects processing
"""

from music_ai_studio import MusicAIStudio


def example_basic_workflow():
    """Basic workflow example."""
    print("=" * 60)
    print("Example 1: Basic Workflow")
    print("=" * 60)
    
    # Initialize studio
    studio = MusicAIStudio(use_chatgpt=False)  # ChatGPT optional
    
    # Set tempo and time signature
    studio.set_studio_tempo(120)
    studio.studio.set_time_signature(4, 4)
    print("✓ Studio configured: 120 BPM, 4/4 time")
    
    # Generate melodic track
    print("\nGenerating melody track...")
    studio.generate_track("track_0", "C D E F G A B C")
    
    # Generate bass track
    print("Generating bass track...")
    studio.generate_track("track_1", "C G C G")
    
    # Mix and display
    mixed = studio.studio.mix()
    print(f"✓ Mixed output: {mixed.shape} stereo samples")
    print(f"   Duration: {mixed.shape[1] / studio.sample_rate:.2f} seconds")


def example_with_chatgpt_direction():
    """Example with ChatGPT creative direction."""
    print("\n" + "=" * 60)
    print("Example 2: ChatGPT Creative Direction")
    print("=" * 60)
    
    try:
        studio = MusicAIStudio(use_chatgpt=True)
        
        # Get creative input from ChatGPT
        if studio.chatgpt:
            print("\n🤖 Asking ChatGPT for creative direction...")
            result = studio.get_music_prompt(
                "Create an upbeat electronic track with a catchy bass line and synth leads"
            )
            
            if "interpretation" in result["stages"]:
                interp = result["stages"]["interpretation"]
                print(f"   Genre: {interp.get('genre')}")
                print(f"   Tempo: {interp.get('tempo')} BPM")
                print(f"   Mood: {interp.get('mood')}")
                print(f"   Instruments: {', '.join(interp.get('instruments', []))}")
    
    except ValueError as e:
        print(f"⚠️  ChatGPT not available: {e}")


def example_effects_processing():
    """Example with effects processing."""
    print("\n" + "=" * 60)
    print("Example 3: Real-time Effects Processing")
    print("=" * 60)
    
    studio = MusicAIStudio()
    
    # Generate lead track
    studio.generate_track("track_0", "E G B E G B")
    print("✓ Generated lead track")
    
    # Apply effects
    print("\nApplying effects...")
    studio.add_effect_to_track("track_0", "reverb", decay=0.5)
    studio.add_effect_to_track("track_0", "delay", delay_time=0.25, feedback=0.3)
    studio.add_effect_to_track("track_0", "compression", threshold=0.6, ratio=4.0)
    
    # Generate bass track with reverb
    studio.generate_track("track_1", "E E E E")
    studio.add_effect_to_track("track_1", "reverb", decay=0.3)
    
    # Mix and show state
    mixed = studio.studio.mix()
    state = studio.get_studio_state()
    
    print(f"\n✓ Final mix created")
    print(f"   Master volume: {state['master_volume']}")
    print(f"   Applied effects in {len(state['tracks'])} tracks")


def example_composition_creation():
    """Example creating a complete composition."""
    print("\n" + "=" * 60)
    print("Example 4: Complete Composition")
    print("=" * 60)
    
    studio = MusicAIStudio(use_chatgpt=False)
    
    # Create composition
    comp = studio.create_composition(
        name="Sunset Dreams",
        description="Ambient electronic with warm pads and soft piano"
    )
    
    print(f"🎼 Composition: {comp['name']}")
    print(f"   Description: {comp['description']}")
    
    # Build the composition
    print("\nBuilding composition...")
    
    # Pad layer (slow moving)
    studio.generate_track("track_0", "C C C C")
    studio.add_effect_to_track("track_0", "reverb", decay=0.7)
    
    # Melody layer
    studio.generate_track("track_1", "E G B D E")
    studio.add_effect_to_track("track_1", "delay", delay_time=0.3)
    
    # Bass layer
    studio.generate_track("track_2", "C G")
    
    # Get final state
    state = studio.get_studio_state()
    print(f"\n✓ Composition complete")
    print(f"   Tracks: {len([t for t in state['tracks'] if not t == 'name'])}")
    print(f"   Tempo: {state['tempo']} BPM")


def example_module_orchestration():
    """Example showing module orchestration."""
    print("\n" + "=" * 60)
    print("Example 5: Module Orchestration")
    print("=" * 60)
    
    studio = MusicAIStudio()
    
    print("\nModules in orchestrator:")
    status = studio.orchestrator.get_module_status()
    for module, state in status.items():
        print(f"   • {module}: {state}")
    
    # Collaborate across modules
    print("\nInitiating module collaboration...")
    result = studio.orchestrator.collaborate_modules(
        "compose",
        {"style": "electronic", "duration_seconds": 60}
    )
    
    print(f"✓ Collaboration complete")
    print(f"   Modules involved: {', '.join(result['modules_involved'])}")
    
    # Check event log
    events = studio.orchestrator.get_event_log(limit=5)
    print(f"\n📋 Recent events ({len(events)}):")
    for event in events[-3:]:
        print(f"   • {event['type']}")


if __name__ == "__main__":
    # Run all examples
    example_basic_workflow()
    example_with_chatgpt_direction()
    example_effects_processing()
    example_composition_creation()
    example_module_orchestration()
    
    print("\n" + "=" * 60)
    print("✓ All examples completed!")
    print("=" * 60)
