/*------------------------------------------------------------------------------
  Formware Over-the_Air - Symbrosia Controller
  - update firmware from a GitHub URL

  02Nov2024 v2.8 A. Cooper
  - initial version

--------------------------------------------------------------------------------

    SymbCtrl - The Symbrosia Aquaculture Controller
    Copyright © 2021 Symbrosia Inc.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
  
------------------------------------------------------------------------------*/

//- library includes -----------------------------------------------------------
#include <Arduino.h>

//- Local includes -------------------------------------------------------------
#include "globals.h"
#include "fotaCtrl.h"
#include <esp32fota.h>

//- constants ------------------------------------------------------------------
const char* manifest= "https://raw.githubusercontent.com/symbrosia-co/Symbrosia-Controller/refs/heads/main/update/update.json";

// root SSL certificate for GitHub
// Issued by: USERTrust ECC Certification Authority
// Valid until: 1/18/38, 1:59:59 PM HST
const char* root_ca= R"ROOT_CA(
-----BEGIN CERTIFICATE-----
MIIDjjCCAnagAwIBAgIQAzrx5qcRqaC7KGSxHQn65TANBgkqhkiG9w0BAQsFADBh
MQswCQYDVQQGEwJVUzEVMBMGA1UEChMMRGlnaUNlcnQgSW5jMRkwFwYDVQQLExB3
d3cuZGlnaWNlcnQuY29tMSAwHgYDVQQDExdEaWdpQ2VydCBHbG9iYWwgUm9vdCBH
MjAeFw0xMzA4MDExMjAwMDBaFw0zODAxMTUxMjAwMDBaMGExCzAJBgNVBAYTAlVT
MRUwEwYDVQQKEwxEaWdpQ2VydCBJbmMxGTAXBgNVBAsTEHd3dy5kaWdpY2VydC5j
b20xIDAeBgNVBAMTF0RpZ2lDZXJ0IEdsb2JhbCBSb290IEcyMIIBIjANBgkqhkiG
9w0BAQEFAAOCAQ8AMIIBCgKCAQEAuzfNNNx7a8myaJCtSnX/RrohCgiN9RlUyfuI
2/Ou8jqJkTx65qsGGmvPrC3oXgkkRLpimn7Wo6h+4FR1IAWsULecYxpsMNzaHxmx
1x7e/dfgy5SDN67sH0NO3Xss0r0upS/kqbitOtSZpLYl6ZtrAGCSYP9PIUkY92eQ
q2EGnI/yuum06ZIya7XzV+hdG82MHauVBJVJ8zUtluNJbd134/tJS7SsVQepj5Wz
tCO7TG1F8PapspUwtP1MVYwnSlcUfIKdzXOS0xZKBgyMUNGPHgm+F6HmIcr9g+UQ
vIOlCsRnKPZzFBQ9RnbDhxSJITRNrw9FDKZJobq7nMWxM4MphQIDAQABo0IwQDAP
BgNVHRMBAf8EBTADAQH/MA4GA1UdDwEB/wQEAwIBhjAdBgNVHQ4EFgQUTiJUIBiV
5uNu5g/6+rkS7QYXjzkwDQYJKoZIhvcNAQELBQADggEBAGBnKJRvDkhj6zHd6mcY
1Yl9PMWLSn/pvtsrF9+wX3N3KjITOYFnQoQj8kVnNeyIv/iPsGEMNKSuIEyExtv4
NeF22d+mQrvHRAiGfzZ0JFrabA0UWTW98kndth/Jsw1HKj2ZL7tcu7XUIOGZX1NG
Fdtom/DzMNU+MeKNhJ7jitralj41E6Vf8PlwUHBHQRFXGU7Aj64GxJUTFy8bJZ91
8rGOmaFvE7FBcf6IKshPECBV1/MUReXgRPTqh5Uykw7+U0b6LJ3/iyK5S9kJRaTe
pLiaWN0bfVKfjllDiIGknibVb63dDcY3fe0Dkhvld1927jyNxF1WW6LZZm6zNTfl
MrY=
-----END CERTIFICATE-----
)ROOT_CA";

//- functions ------------------------------------------------------------------
FOtACtrl::FOtACtrl(){
}

int FOtACtrl::update(){
  if (!wifiStat) return 1;
  Serial.println("  Updating firmware...");
  char version[12];
  char fwMaj[5];
  char fwMin[5];
  ultoa(firmMajor,fwMaj,10);
  ultoa(firmMinor,fwMin,10);
  strcpy(version,fwMaj);
  strcat(version,".");
  strcat(version,fwMin);
  strcat(version,".0");
#ifdef hardwareS2Mini
  esp32FOTA esp32FOTA("SymbCtrl-Mk2-S2",version,false,false);
#endif
#ifdef hardwareS3Mini
  esp32FOTA esp32FOTA("SymbCtrl-Mk2-S3",version,false,false);
#endif
  esp32FOTA.setManifestURL(manifest);
  esp32FOTA.useDeviceId(true);
  CryptoMemAsset *LocalRootCA= new CryptoMemAsset("Root CA",root_ca,strlen(root_ca)+1);
  esp32FOTA.setRootCA(LocalRootCA);
  if (esp32FOTA.execHTTPcheck()){
    Serial.println("  Version checked, update required");
    if (esp32FOTA.execOTA()) return fotaComplete;
    return fotaFailed;
  }
  Serial.println("  No update required!");
  return fotaNotReq;
} // update

//- End fotaCtrl ----------------------------------------------------------------
