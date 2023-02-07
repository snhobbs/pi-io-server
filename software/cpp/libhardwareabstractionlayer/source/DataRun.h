#include <cstdint>
#include <vector>
#include <tuple>
#include "RunConfig.h"
using AdcDataType = std::vector<std::tuple<uint16_t, uint16_t, uint16_t, uint16_t>>;
void LedSwToggle(const uint32_t start_value, const uint32_t frequency);
AdcDataType AdcRead(const uint32_t adc_frequency, const uint32_t enabled_adcs,
        const uint32_t kReadings);
AdcDataType StartDataRun(const RunConfig &run_config);
void SetupHardware();
void WriteDacs(const RunConfig& run_config);

