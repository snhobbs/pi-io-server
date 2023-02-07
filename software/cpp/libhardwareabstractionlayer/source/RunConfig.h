#pragma once
#include <map>
#include <sstream>
#include <iostream>
#include <fstream>
#include <string>
#include <algorithm>

enum class FieldType {
  kWhiteLed,
  kRedLed,
  kBlueLed,
  kGreenLed,
  kIrLed,
  kBulb12,
  kBulb24,
  kAdcFrequency,
  kAdcReadings,
  kLedSWFrequency,
  kLedSWLevel,
};

inline bool FileExists(const std::string &name) {
  std::ifstream f(name.c_str());
  return f.good();
}

class RunConfig {
 public:
  bool FieldExists(const FieldType field) const {
    auto str_key_it = field_names_.find(field);
    return entries_.find(str_key_it->second) != entries_.end();
  }

  uint32_t GetField(const FieldType field) const {
    if (!FieldExists(field)) {
      return 0;
    }
    auto str_key_it = field_names_.find(field);
    return entries_.find(str_key_it->second)->second;
  }

  const std::map<FieldType, std::string> get_field_names(void) const {
    return field_names_;
  }

  bool AllFieldsPresent(void) const {
    for (auto pt : get_field_names()) {
      if (!FieldExists(pt.first)) {
        std::cout << "Missing field " << pt.second << std::endl;
        return false;
      }
    }
    return true;
  }

  explicit RunConfig(const std::map<std::string, std::string> &args) {
    for (auto pt : args) {
      std::string key{pt.first};
      std::transform(key.begin(), key.end(), key.begin(), ::tolower);
      entries_.insert(std::pair{key, std::atoll(pt.second.c_str())});
    }
  }

 private:
  const std::map<FieldType, std::string> field_names_{
      {FieldType::kWhiteLed, "white led setting"},
      {FieldType::kRedLed, "red led setting"},
      {FieldType::kBlueLed, "blue led setting"},
      {FieldType::kGreenLed, "green led setting"},
      {FieldType::kIrLed, "ir led setting"},
      {FieldType::kBulb12, "12v bulb setting"},
      {FieldType::kBulb24, "24v bulb setting"},
      {FieldType::kAdcReadings, "adc readings"},
      {FieldType::kAdcFrequency, "adc frequency"},
      {FieldType::kLedSWFrequency, "ledsw frequency"},
      {FieldType::kLedSWLevel, "ledsw starting value"},
  };
  std::map<std::string, uint32_t> entries_;
};

inline int ReadFileToMap(std::map<std::string, std::string> *key_pairs,
                  std::string file_name) {
  std::fstream file{file_name};
  std::string line;
  while (std::getline(file, line)) {
    std::istringstream line_stream{line};
    std::string key;
    std::string value;

    // Skip any line without a semi colon
    if (std::getline(line_stream, key, ':')) {
      std::getline(line_stream, value);
      key_pairs->insert(std::pair{key, value});
    }
  }
  return 0;
}

