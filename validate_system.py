#!/usr/bin/env python
"""
System validation and integration test.

Verifies all modular components are working correctly.
"""

import sys
from pathlib import Path


def test_imports():
    """Test all module imports."""
    print("🔍 Testing module imports...")

    try:
        from music_ai_core import (
            load_audio,
            mel_spectrogram,
            SimpleAutoencoder,
            LiveMusicStudio,
            InstrumentSynthesizer,
            EffectsProcessor,
            ChatGPTModule,
            ModuleOrchestrator,
            get_default_config
        )
        # Verify the imports are the expected types
        assert callable(load_audio)
        assert callable(mel_spectrogram)
        assert callable(SimpleAutoencoder)
        assert callable(LiveMusicStudio)
        assert callable(InstrumentSynthesizer)
        assert callable(EffectsProcessor)
        assert callable(ChatGPTModule)
        assert callable(ModuleOrchestrator)
        assert callable(get_default_config)
        print("   ✓ All imports successful")
        return True
    except ImportError as e:
        print(f"   ✗ Import error: {e}")
        return False


def test_live_studio():
    """Test live studio functionality."""
    print("\n🎛️  Testing Live Studio...")

    try:
        from music_ai_core import LiveMusicStudio

        studio = LiveMusicStudio(sample_rate=44100, num_tracks=8)
        print("   ✓ Studio initialized")

        # Generate track
        studio.generate_track("track_0", [(440, 0.5), (880, 0.5)])
        print("   ✓ Track generated")

        # Apply effects
        studio.apply_effect("track_0", "reverb", decay=0.5)
        print("   ✓ Reverb applied")

        # Mix
        mixed = studio.mix()
        print(f"   ✓ Mixed audio: {mixed.shape}")

        # Get state
        state = studio.get_studio_state()
        print(f"   ✓ Studio state: {state['num_tracks']} tracks, {state['tempo']} BPM")

        return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def test_orchestrator():
    """Test module orchestrator."""
    print("\n🎼 Testing Module Orchestrator...")

    try:
        from music_ai_core import ModuleOrchestrator, LiveMusicStudio

        orchestrator = ModuleOrchestrator()
        print("   ✓ Orchestrator initialized")

        studio = LiveMusicStudio()
        orchestrator.register_module("studio", studio)
        print("   ✓ Module registered")

        status = orchestrator.get_module_status()
        print(f"   ✓ Module status: {status}")

        info = orchestrator.get_system_info()
        print(f"   ✓ System info: {info['module_count']} modules")

        return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def test_configuration():
    """Test configuration system."""
    print("\n⚙️  Testing Configuration...")

    try:
        from music_ai_core.config import SystemConfig, get_default_config

        config = get_default_config()
        print("   ✓ Default config created")

        config_dict = config.get_config_dict()
        print(f"   ✓ Config dict: {len(config_dict)} sections")

        # Test file I/O
        test_path = "/tmp/test_config.json"
        config.save_to_file(test_path)
        print(f"   ✓ Config saved to {test_path}")

        config2 = SystemConfig()
        config2.load_from_file(test_path)
        print("   ✓ Config loaded from file")

        # Cleanup
        Path(test_path).unlink(missing_ok=True)

        return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def test_synthesizer():
    """Test instrument synthesizer."""
    print("\n🎹 Testing Instrument Synthesizer...")

    try:
        from music_ai_core import InstrumentSynthesizer

        synth = InstrumentSynthesizer()
        print("   ✓ Synthesizer initialized")

        # Generate notes
        for waveform in ["sine", "square", "sawtooth", "triangle"]:
            audio = synth.synthesize_note(440, 0.5, waveform=waveform)
            print(f"   ✓ Generated {waveform} wave: {audio.shape}")

        return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def test_effects():
    """Test effects processor."""
    print("\n🎚️  Testing Effects Processor...")

    try:
        import numpy as np
        from music_ai_core import EffectsProcessor

        effects = EffectsProcessor()
        print("   ✓ Effects processor initialized")

        # Create test audio
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, 44100))

        # Test effects
        effects.add_reverb(audio)
        print("   ✓ Reverb applied")

        effects.add_delay(audio)
        print("   ✓ Delay applied")

        effects.add_compression(audio)
        print("   ✓ Compression applied")

        effects.normalize(audio)
        print("   ✓ Normalization applied")

        return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def test_chatgpt_module():
    """Test ChatGPT module."""
    print("\n🤖 Testing ChatGPT Module...")

    try:
        from music_ai_core import ChatGPTModule

        # Try to initialize (will fail if no API key, but that's OK for this test)
        try:
            chatgpt = ChatGPTModule()
            print("   ✓ ChatGPT module initialized")

            # Test interpretation
            result = chatgpt.interpret_music_prompt("upbeat electronic")
            print(f"   ✓ Interpretation: {result['genre']} @ {result['tempo']} BPM")

            return True
        except ValueError as e:
            print(f"   ⚠️  ChatGPT module skipped (no API key): {e}")
            return True  # Not a failure - API key is optional
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def test_main_application():
    """Test main music AI studio application."""
    print("\n🎵 Testing Music AI Studio Application...")

    try:
        from music_ai_studio import MusicAIStudio

        studio = MusicAIStudio(use_chatgpt=False)
        print("   ✓ Studio application initialized")

        studio.set_studio_tempo(140)
        print("   ✓ Tempo set to 140 BPM")

        studio.generate_track("track_0", "C D E F G")
        print("   ✓ Track generated from notes")

        studio.add_effect_to_track("track_0", "reverb", decay=0.6)
        print("   ✓ Effect applied")

        state = studio.get_studio_state()
        print(f"   ✓ Studio state retrieved: {state}")

        return True
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False


def run_all_tests():
    """Run all validation tests."""
    print("=" * 60)
    print("🔬 Music AI Studio - System Validation")
    print("=" * 60)

    tests = [
        ("Imports", test_imports),
        ("Live Studio", test_live_studio),
        ("Orchestrator", test_orchestrator),
        ("Configuration", test_configuration),
        ("Synthesizer", test_synthesizer),
        ("Effects", test_effects),
        ("ChatGPT Module", test_chatgpt_module),
        ("Main Application", test_main_application),
    ]

    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n✗ Unexpected error in {name}: {e}")
            results.append((name, False))

    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8s} {name}")

    print("-" * 60)
    print(f"Result: {passed}/{total} tests passed")

    if passed == total:
        print("\n✓ All systems operational! Ready for music production. 🎵")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed. Please check errors above.")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
