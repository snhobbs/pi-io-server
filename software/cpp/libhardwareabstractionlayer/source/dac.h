#include <stdint.h>
#include <stdbool.h>
#if 0 
#include <EmitterBoard/Hardware.h>

enum class Channel : uint16_t{
  kCh0,
  kCh1,
  kCh2,
  kCh3,
  kCh4,
  kCh5,
  kCh6,
  kCh7,
  kNone,
};

inline const constexpr std::array<Channel, 8> kDacChannels {
	Channel::kCh0,
	Channel::kCh1,
	Channel::kCh2,
	Channel::kCh3,
	Channel::kCh4,
	Channel::kCh5,
	Channel::kCh6,
	Channel::kCh7
};
inline constexpr Channel EmitterToChannel(const Emitter emitter) {
  return static_cast<Channel>(static_cast<uint32_t>(emitter));
}
#endif
void DacSetup(void);
void DacWrite(const uint16_t write_code, const uint8_t value);
void DacWriteChannel(const uint16_t channel, const uint8_t value);
