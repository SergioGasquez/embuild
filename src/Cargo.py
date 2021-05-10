# Cargo <-> PlatformIO integration script (autogenerated by cargo-pio)
# Calling 'pio run' will also build the Rust library crate by invoking Cargo

import os

Import("env")

def run_cargo(source, target, env):
    def get_mcu():
        board_mcu = env.get("BOARD_MCU")
        if not board_mcu and "BOARD" in env:
            board_mcu = env.BoardConfig().get("build.mcu")

        return board_mcu

    def derive_rust_target():
        mcu = get_mcu()

        if mcu.startswith("32mx") or mcu.startswith("32mz"):
            # 32 bit PIC
            return "mipsel-unknown-none"
        elif mcu.startswith("msp430"):
            # MSP-430
            return "msp430-none-elf"
        elif mcu.startswith("at90") or mcu.startswith("atmega") or mcu.startswith("attiny"):
            # Microchip AVR
            return "avr-unknown-gnu-atmega328"
        elif mcu.startswith("efm32"):
            # ARM Cortex-M4
            return "thumbv7em-none-eabi"
        elif mcu.startswith("lpc"):
            # ARM Cortex-M0
            return "thumbv6m-none-eabi"
        elif mcu == "esp32":
            # ESP32
            return "xtensa-esp32-none-elf"
        elif mcu == "esp32s2":
            # ESP32S2
            return "xtensa-esp32s2-none-elf"
        elif mcu == "esp8266":
            # ESP8266
            return "xtensa-esp8266-none-elf"
        elif mcu.startsWith("stm32f7") or mcu.startsWith("stm32h7"):
            # ARM Cortex-M7F
            return "thumbv7em-none-eabihf"
        elif mcu.startsWith("stm32f3") or mcu.startsWith("stm32f4") or mcu.startsWith("stm32g4") or mcu.startsWith("stm32l4") or mcu.startsWith("stm32l4+"):
            # ARM Cortex-M4F
            return "thumbv7em-none-eabihf"
        elif mcu.startsWith("stm32g0") or mcu.startsWith("stm32l0") or mcu.startsWith("stm32f0"):
            # ARM Cortex-M0/M0+
            return "thumbv6m-none-eabi"
        else:
            print(f"Cannot derive Rust target triple for MCU {mcu}. "
                "Specify the Rust target manually in platformio.ini using parameter rust_target = \"<rust-target-triple>\"")
            Exit(2)

        return target

    rust_lib = env.GetProjectOption("rust_lib")

    rust_target = env.GetProjectOption("rust_target", default = {})
    if rust_target == {}:
        rust_target = derive_rust_target()

    cargo_options = env.GetProjectOption("cargo_options", default = "")

    cargo_profile = env.GetProjectOption(
        "cargo_profile",
        default = "release" if env.GetProjectOption("build_type") == "release" else "debug")

    cargo_target_dir = env.GetProjectOption(
        "cargo_target_dir",
        default = os.path.join("$PROJECT_BUILD_DIR", "cargo")
            if env.GetProjectOption("cargo_pio_common_build_dir", default = False)
            else os.path.join("$PROJECT_DIR", "target"))

    env["ENV"]["BINDGEN_INC_FLAGS"] = env.subst("$_CPPINCFLAGS")

    if env.Execute(f"cargo build {'--release' if cargo_profile == 'release' else ''} --lib --target {rust_target} {cargo_options}"):
        Exit(1)

    env.Prepend(LIBPATH = [os.path.join(cargo_target_dir, rust_target, cargo_profile)])
    #env.Prepend(LIBS = [rust_lib])
    # The code below is a bit of a hack so that GCC intrinsics take precedence over Rust intrinsics
    # and most importantly, workaround the linker complaining that there are duplicate definitions of those
    # See here for more information: https://stackoverflow.com/questions/63950040/multiple-definition-of-aeabi-ul2f-on-android-ndk-libgcc-real-a
    # Alternative (and more hacky) approach: https://stackoverflow.com/questions/61931313/multiple-definition-of-udivti3-in-libgcc-and-rust-system-library
    env.Append(LINKFLAGS = "-l" + rust_lib)

env.AddPreAction(os.path.join("$BUILD_DIR", env.subst("$PROGNAME$PROGSUFFIX")), run_cargo)
