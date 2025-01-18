# Control Panel

Mainly for script execution on slave PC(s), with misc monitoring.

Master serves webui for script execution on slaves.

### To Install

```
cd front
npm install react-scripts
cd ../master
./build_front.sh
```

Then:

- Move Master and Slave folders to appropriate PCs.
- Add both run.sh from respective folders to systemctl for statup execution.

### Dev (Single PC)

Frontend:

```
npm install react-scripts
npm start
```

Master:

```
./run.sh --dev
```

Slave:

```
./run.sh --dev
```
