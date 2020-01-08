# Secure-Smartphone

This repository contains an implementation of the S.A.T.A.N. (Smartphone As A Security Token) project, for the 2017/2018 **Network and Computer Security** course
at **Instituto Superior Técnico**.

## Project Description

This project aims at creating a security mobile android application that handles the access of a secure folder in a desktop computer.

Project report at Report/A 10 3 1530 7 report.pdf

## Problem
Only those with access to both the paired phone and computer can access the encrypted files in the secure folcer.

## Requirements
1. Confidentiality (only the paired computer can read the security token)
2. Authentication of origin (the paired computer only accepts tokens sent by the paired phone, replay and man in the middle attacks protection)
3. Fault tolerance (if the computer crashes when the computer is connected,
the files cannot be left unprotected)

## Protocol
All keys are securely stored.
Pairing
1. Initial pairing fase between the Android application and the PC application through the exchange of a QR code containing a RSA public key of the PC.
2. After the Android stores the PC RSA public key, the Android shares with PC, encrypted with the PC's RSA public key, an AES-256 session key.
3. Android sends to PC, encrypted with the session key, its own RSA public key, which the PC stores.
4. Android generates two other AES-256 keys, one to be used for the secure folder encryption (A), and one to encrypt the previous key (B).
5. Android stores the B key and sends the A key and the A key encrypted with the B key to the PC.
6. PC uses A key to encrypt the secure folder and destroys it, storing only the A key encrypted with the B key. Now only the Android has the B key, and the computer contains the encrypted A key. To desencrypt its files the computer needs the smartphone A key.

Heartbeat
1. New session key exchange between the PC and the Android using the RSA keys for the initial comunication.
2. Using the new session key, the PC sends the encrypted A key for the Android to desencrypt it.
3. The Android sends back the desencrypted A key to the PC so it can use it do desencrypt the files.
4. Now the Android will send unique heartbeats to the PC to declare its presence.
5. Once the Android ceases its heartbeats, because it went out of range for example, the PC will encrypt the files again and destroy the decrypted A key.
6. In case of a crash, after recovery it will encrypt all the files with the decrypted A key, then deletes the key and waits for the phone to be reconnected.