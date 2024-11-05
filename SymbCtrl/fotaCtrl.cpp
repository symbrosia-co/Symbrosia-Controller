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
#include <WiFi.h>

//- constants ------------------------------------------------------------------
const char* manifest= "https://raw.githubusercontent.com/symbrosia-co/Symbrosia-Controller/refs/heads/main/update/update.json";

// root SSL certificate for GitHub
// Issued by: USERTrust ECC Certification Authority
// Valid until: 1/18/38, 1:59:59 PM HST
const char* root_ca= R"ROOT_CA(
-----BEGIN CERTIFICATE-----
MIICjzCCAhWgAwIBAgIQXIuZxVqUxdJxVt7NiYDMJjAKBggqhkjOPQQDAzCBiDEL
MAkGA1UEBhMCVVMxEzARBgNVBAgTCk5ldyBKZXJzZXkxFDASBgNVBAcTC0plcnNl
eSBDaXR5MR4wHAYDVQQKExVUaGUgVVNFUlRSVVNUIE5ldHdvcmsxLjAsBgNVBAMT
JVVTRVJUcnVzdCBFQ0MgQ2VydGlmaWNhdGlvbiBBdXRob3JpdHkwHhcNMTAwMjAx
MDAwMDAwWhcNMzgwMTE4MjM1OTU5WjCBiDELMAkGA1UEBhMCVVMxEzARBgNVBAgT
Ck5ldyBKZXJzZXkxFDASBgNVBAcTC0plcnNleSBDaXR5MR4wHAYDVQQKExVUaGUg      
VVNFUlRSVVNUIE5ldHdvcmsxLjAsBgNVBAMTJVVTRVJUcnVzdCBFQ0MgQ2VydGlm
aWNhdGlvbiBBdXRob3JpdHkwdjAQBgcqhkjOPQIBBgUrgQQAIgNiAAQarFRaqflo
I+d61SRvU8Za2EurxtW20eZzca7dnNYMYf3boIkDuAUU7FfO7l0/4iGzzvfUinng
o4N+LZfQYcTxmdwlkWOrfzCjtHDix6EznPO/LlxTsV+zfTJ/ijTjeXmjQjBAMB0G
A1UdDgQWBBQ64QmG1M8ZwpZ2dEl23OA1xmNjmjAOBgNVHQ8BAf8EBAMCAQYwDwYD
VR0TAQH/BAUwAwEB/zAKBggqhkjOPQQDAwNoADBlAjA2Z6EWCNzklwBBHU6+4WMB
zzuqQhFkoJ2UOQIReVx7Hfpkue4WQrO/isIJxOzksU0CMQDpKmFHjFJKS04YcPbW
RNZu9YO6bVi9JNlWSOrvxKJGgYhqOkbRqZtNyWHa0V1Xahg=
-----END CERTIFICATE-----
)ROOT_CA";

//- functions ------------------------------------------------------------------
FOtACtrl::FOtACtrl(){
}

void FOtACtrl::update(){
  Serial.println("  Updating firmware...");
  char version[12];
  char fwMaj[5];
  char fwMin[5];
  const char dot[]= ".";
  ultoa(firmMajor,fwMaj,10);
  ultoa(firmMinor,fwMin,10);
  strcpy(version,fwMaj);
  strcat(version,dot);
  strcat(version,fwMin);
#ifdef hardwareS2Mini
  esp32FOTA esp32FOTA("SymbCtrl-Mk2-S2",version,false);
#endif
#ifdef hardwareS3Mini
  esp32FOTA esp32FOTA("SymbCtrl-Mk2-S3",version,false);
#endif
  CryptoMemAsset *LocalRootCA= new CryptoMemAsset("Root CA",root_ca,strlen(root_ca)+1);
  esp32FOTA.setRootCA(LocalRootCA);
  esp32FOTA.setManifestURL(manifest);
  esp32FOTA.useDeviceId(true);
  //esp32FOTA.setProgressCb([](size_t progress, size_t size) {if(progress==size || progress==0) Serial.println(progress);Serial.print(".");});
  //esp32FOTA.setUpdateEndCb([](int partition){Serial.printf("Update could not finish with %s partition\n", partition==U_SPIFFS ? "spiffs" : "firmware" );});
  //esp32FOTA.setUpdateFinishedCb([](int partition, bool restart_after){Serial.printf("Update could not begin with %s partition\n", partition==U_SPIFFS ? "spiffs" : "firmware" );if( restart_after ){ESP.restart();}});
  Serial.print("  Current: ");Serial.println(version);
  Serial.print("  Update:  ");Serial.println(esp32FOTA.getPayloadVersion());
  Serial.print("  Manifest:");Serial.println(esp32FOTA.getManifestURL());
  Serial.print("  Firmware:");Serial.println(esp32FOTA.getFirmwareURL());
  if (esp32FOTA.execHTTPcheck()){
    Serial.println("  Version checked, update required");
    esp32FOTA.execOTA();
  }
  else Serial.println("  No update required!");
} // update

//- End fotaCtrl ----------------------------------------------------------------
