function Image(el)
  -- Check for width/height attributes from HTML export
  local width = el.attributes["width"]
  local height = el.attributes["height"]

  -- Ensure image is embedded at full resolution, but scaled visually
  if width then
    el.attributes["style"] = "width:" .. width .. "px"
    el.attributes["width"] = nil
  end

  if height then
    if el.attributes["style"] then
      el.attributes["style"] = el.attributes["style"] .. ";height:" .. height .. "px"
    else
      el.attributes["style"] = "height:" .. height .. "px"
    end
    el.attributes["height"] = nil
  end

  return el
end
