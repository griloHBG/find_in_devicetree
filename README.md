# find-in-devicetree

## Dependencies

Python packages:
- colorit (`python3 -m pip install color-it`)
- gitpython (`python3  -m pip install gitpython`)

## Overview

find_in_devicetree is a python script that recursively "crawls" the includes of a `.dts`/`.dtsi` file searching for one or more regular expression(s) (regex / regexp) and returns its findings explicitly showing the files where the regex(s) was(were) found and in which lines. 

## Usage example

```
$ # Be sure to be inside the root path of a Linux Kernel source code repository
$ cd linux-toradex
$ # Now we can search for any regexp string in a devicetree set of files by targetting a .dts or a .dtsi file
$ find-in-dt arch/arm64/boot/dts/freescale/imx8mm-verdin-wifi-dev.dts iomuxc\s*[:-]
/path/to/linux-toradex
search_in: all, returning: all
searching in:
        /path/to/linux-toradex/include/dt-bindings/pwm/pwm.h
        /path/to/linux-toradex/include/dt-bindings/clock/imx8mm-clock.h
        /path/to/linux-toradex/include/dt-bindings/reset/imx8mq-reset.h
        /path/to/linux-toradex/include/dt-bindings/gpio/gpio.h
        /path/to/linux-toradex/include/dt-bindings/input/input.h
        /path/to/linux-toradex/include/dt-bindings/interrupt-controller/arm-gic.h
        /path/to/linux-toradex/include/dt-bindings/reset/imx8mm-dispmix.h
        /path/to/linux-toradex/include/dt-bindings/thermal/thermal.h
        /path/to/linux-toradex/arch/arm64/boot/dts/freescale/imx8mm-pinfunc.h
        /path/to/linux-toradex/include/dt-bindings/input/linux-event-codes.h
        /path/to/linux-toradex/include/dt-bindings/interrupt-controller/irq.h
        /path/to/linux-toradex/arch/arm64/boot/dts/freescale/imx8mm-verdin.dtsi
        /path/to/linux-toradex/arch/arm64/boot/dts/freescale/imx8mm-verdin-wifi.dtsi
        /path/to/linux-toradex/arch/arm64/boot/dts/freescale/imx8mm-verdin-dev.dtsi
        /path/to/linux-toradex/arch/arm64/boot/dts/freescale/imx8mm.dtsi
        /path/to/linux-toradex/arch/arm64/boot/dts/freescale/imx8mm-verdin-dahlia.dtsi
        /path/to/linux-toradex/arch/arm64/boot/dts/freescale/imx8mm-verdin-wifi-dev.dts
findings:
/path/to/linux-toradex/arch/arm64/boot/dts/freescale/imx8mm.dtsi
        657 :                   iomuxc: pinctrl@30330000 {
        662 :                   gpr: iomuxc-gpr@30340000 {
        663 :                           compatible = "fsl,imx8mm-iomuxc-gpr", "fsl,imx6q-iomuxc-gpr", "syscon";
        1192 :                          compatible = "fsl, imx8mm-iomuxc-gpr", "syscon";

search_in: all, returning: all
----------------------------------------------------------------------------------------------------

$ # Another example
 $ find-in-dt arm64/boot/dts/freescale/imx8mm-verdin-wifi-dev.dts "pinctrl_uart\d"
/path/to/linux-toradex/arch
search_in: all, returning: all
searching in:
        /path/to/linux-toradex/include/dt-bindings/pwm/pwm.h
        /path/to/linux-toradex/include/dt-bindings/clock/imx8mm-clock.h
        /path/to/linux-toradex/include/dt-bindings/reset/imx8mq-reset.h
        /path/to/linux-toradex/include/dt-bindings/gpio/gpio.h
        /path/to/linux-toradex/include/dt-bindings/input/input.h
        /path/to/linux-toradex/include/dt-bindings/interrupt-controller/arm-gic.h
        /path/to/linux-toradex/include/dt-bindings/reset/imx8mm-dispmix.h
        /path/to/linux-toradex/include/dt-bindings/thermal/thermal.h
        /path/to/linux-toradex/arch/arm64/boot/dts/freescale/imx8mm-pinfunc.h
        /path/to/linux-toradex/include/dt-bindings/input/linux-event-codes.h
        /path/to/linux-toradex/include/dt-bindings/interrupt-controller/irq.h
        /path/to/linux-toradex/arch/arm64/boot/dts/freescale/imx8mm-verdin.dtsi
        /path/to/linux-toradex/arch/arm64/boot/dts/freescale/imx8mm-verdin-wifi.dtsi
        /path/to/linux-toradex/arch/arm64/boot/dts/freescale/imx8mm-verdin-dev.dtsi
        /path/to/linux-toradex/arch/arm64/boot/dts/freescale/imx8mm.dtsi
        /path/to/linux-toradex/arch/arm64/boot/dts/freescale/imx8mm-verdin-dahlia.dtsi
        /path/to/linux-toradex/arch/arm64/boot/dts/freescale/imx8mm-verdin-wifi-dev.dts
findings:
/path/to/linux-toradex/arch/arm64/boot/dts/freescale/imx8mm-verdin.dtsi
        710 :   pinctrl-0 = <&pinctrl_uart1>;
        716 :   pinctrl-0 = <&pinctrl_uart2>;
        723 :   pinctrl-0 = <&pinctrl_uart3>;
        734 :   pinctrl-0 = <&pinctrl_uart4>;
        1187 :  pinctrl_uart1: uart1grp {
        1194 :  pinctrl_uart2: uart2grp {
        1203 :  pinctrl_uart3: uart3grp {
        1212 :  pinctrl_uart4: uart4grp {

search_in: all, returning: all
----------------------------------------------------------------------------------------------------
```

### find_in_dt overview
![img.png](images/find_in_dt.png)
