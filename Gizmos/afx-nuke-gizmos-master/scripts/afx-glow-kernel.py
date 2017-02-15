# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
# Copyright (C) 2012-2017, Ryan P. Wilson
#
#      Authority FX, Inc.
#      www.authorityfx.com

# Python script to create AFXGlow kernel using native nuke nodes
# Glow kernel code ported from https://github.com/AuthorityFX/afx-nuke-plugins/blob/master/include/glow.h

g = nuke.nodes.Group()
g.setName("AFXGlow")
g.begin()

n = nuke.nodes.NoOp()
n.setName("GlowCtrls")

k = nuke.Double_Knob("exposure", "Exposure")
n.addKnob(k)
k.setRange(-5, 5)
k.setDefaultValue([0])

k = nuke.Double_Knob("threshold", "Threshold")
n.addKnob(k)
k.setRange(0, 1)
k.setDefaultValue([1])

k = nuke.Double_Knob("threshold_falloff", "Threshold Falloff")
n.addKnob(k)
k.setRange(0, 1)
k.setDefaultValue([0.25])

k = nuke.Double_Knob("size", "Glow Size")
n.addKnob(k)
k.setRange(0, 500)
k.setDefaultValue([250])

k = nuke.Double_Knob("softness", "Softness")
n.addKnob(k)
k.setRange(0, 1)
k.setDefaultValue([0])

k = nuke.Double_Knob("diffusion", "Diffusion")
n.addKnob(k)
k.setRange(0, 1)
k.setDefaultValue([0.5])

k = nuke.Double_Knob("quality", "Quality")
n.addKnob(k)
k.setRange(0, 1)
k.setDefaultValue([0.5])

k = nuke.Boolean_Knob("replicate", "Replicate Border")
n.addKnob(k)
k.setDefaultValue([0])

k = nuke.Boolean_Knob("expand_box", "Expand Box")
n.addKnob(k)
k.setDefaultValue([0])


n = nuke.nodes.Crop()
n["box"].setExpression('''[python -execlocal {import math
n = nuke.toNode("GlowCtrls")

size = n.knob("size").value()
softness = n.knob("softness").value()
diffusion = n.knob("diffusion").value()
quality= n.knob("quality").value()

inner_size = (1.0 + 5.0 * softness) / 6.0
max_size = 3
for i in range(0, 50):
    lookup = i / 49.0
    mapped_quality = math.cos(math.pi * 0.5 * lookup) * (1.0 - quality) + quality
    sigma = pow(lookup, 1.0 / diffusion) * (max(size, inner_size) - inner_size) + inner_size
    gauss_size = (int)(math.ceil(sigma * mapped_quality * (6.0 - 1.0) + 1.0)) | 1
    max_size = max(max_size, gauss_size)
    
ret = max_size - 1}]''', 2)
n["box"].setValue(0, 0)
n["box"].setValue(0, 1)
n["box"].setExpression("box.r", 3)
n["reformat"].setValue(1)


iterations = 50
kernels = []

for i in range(0, iterations):
  
    kernels.append(nuke.nodes.Expression())
    
    kernels[i].setName("kernel_1")
    kernels[i]["channel0"].setValue("none")
    kernels[i]["channel1"].setValue("none")
    kernels[i]["channel2"].setValue("none")
    kernels[i]["channel3"].setValue("alpha")
    
    kernels[i]["temp_name0"].setValue("inner_size")
    kernels[i]["temp_expr0"].setValue("(1.0 + 5.0 * GlowCtrls.softness) / 6.0")
    kernels[i]["temp_name1"].setValue("sigma")
    kernels[i]["temp_expr1"].setValue("pow(" + str(i / (iterations - 1.0)) + ", 1/GlowCtrls.diffusion) * (max(GlowCtrls.size, inner_size) - inner_size) + inner_size")
    kernels[i]["temp_name2"].setValue("s2")
    kernels[i]["temp_expr2"].setValue("2 * sigma * sigma")
    kernels[i]["temp_name3"].setValue("a2")
    kernels[i]["temp_expr3"].setValue("1 / pow(sigma * sqrt(2 * pi()), 2.0)")
    
    kernels[i]["expr3"].setValue("a2 * exp(-pow(x - (width / 2), 2) / s2) * exp(-pow(y - (height / 2), 2) / s2)")
    
    kernels[i].setInput(0, n)
    
m = nuke.nodes.Merge2()
m["operation"].setValue("plus")
i = 0
for k in kernels:
    if i == 2:
        i += 1
    m.setInput(i, k)
    i += 1
    
    
g.end()