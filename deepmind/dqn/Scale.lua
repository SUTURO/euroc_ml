--[[
Copyright (c) 2014 Google Inc.

See LICENSE file for full terms of limited license.
]]

require "nn"
require "image"

local scale = torch.class('nn.Scale', 'nn.Module')
local scaleWin = nil

function scale:__init(height, width)
    self.height = height
    self.width = width
end

function scale:forward(x)
    local x = x
    if x:dim() > 3 then
        x = x[1]
    end

    x = image.rgb2y(x)
    x = image.scale(x, self.width, self.height, 'bilinear')
    scaleWin = image.display({image=x, win=scaleWin})
    return x
end

function scale:updateOutput(input)
    return self:forward(input)
end

function scale:float()
end
