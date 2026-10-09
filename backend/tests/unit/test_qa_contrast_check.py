"""The QA contrast check: text whose colour is almost its background's is a defect the one rework is told about."""
from onboarding import qa_contrast_check as cc


def _sample(text, color, background):
    return {"text": text, "color": color, "background": background}


def test_contrast_is_the_ratio_of_the_two_luminances():
    """Verify the ratio is the standard one.

    id: TST-QA-CONTRAST-001
    Given: Black on white, a colour on itself, and two near-white tones
    When: Their contrast is computed
    Then: 21, 1, and a value just above 1, whichever of the two is given first
    """
    assert round(cc.contrast_ratio([0, 0, 0], [255, 255, 255]), 1) == 21.0
    assert cc.contrast_ratio([120, 80, 40], [120, 80, 40]) == 1.0
    near = cc.contrast_ratio([245, 245, 244], [254, 243, 199])
    assert 1.0 <= near < 1.1 and near == cc.contrast_ratio([254, 243, 199], [245, 245, 244])


def test_text_the_tone_of_its_background_is_a_defect_named_with_both_colours():
    """Verify the rework is told what cannot be read, and on what.

    id: TST-QA-CONTRAST-002
    Given: Sixteen texts in a near-white colour on a near-white background, and a readable heading
    When: The verdict is drawn
    Then: One defect: it names the device, how many texts, a few of them, both colours and the contrast measured;
          the readable heading is not in it
    """
    samples = [_sample(f"P{i}", [245, 245, 244], [254, 243, 199]) for i in range(16)]
    samples.append(_sample("Heading", [28, 25, 23], [254, 243, 199]))
    check = cc.verdict_from_samples("Desktop", samples)
    assert len(check.defects) == 1
    defect = check.defects[0]
    assert defect.startswith("[Desktop]") and "16 text(s)" in defect
    assert "#f5f5f4" in defect and "#fef3c7" in defect and "1.0" in defect
    assert '"P0"' in defect and "Heading" not in defect


def test_muted_text_that_can_still_be_read_is_left_alone():
    """Verify the check only speaks when text is all but invisible.

    id: TST-QA-CONTRAST-003
    Given: Grey helper text on white (a contrast near 2.5) and nothing fainter
    When: The verdict is drawn
    Then: No defect
    """
    check = cc.verdict_from_samples("Desktop", [_sample("optional", [163, 163, 163], [255, 255, 255])])
    assert check.defects == []


def test_each_pair_of_colours_is_reported_once():
    """Verify one cause gives one line, however many texts it touches.

    id: TST-QA-CONTRAST-004
    Given: Faint texts in two different colour pairs
    When: The verdict is drawn
    Then: Two defects, the pair touching more texts first
    """
    samples = [_sample("a", [250, 250, 250], [255, 255, 255])]
    samples += [_sample(t, [20, 20, 20], [30, 30, 30]) for t in ("b", "c")]
    check = cc.verdict_from_samples("Mobile", samples)
    assert len(check.defects) == 2 and "2 text(s)" in check.defects[0] and "1 text(s)" in check.defects[1]


def test_a_background_carrying_light_and_dark_text_is_asked_to_be_a_middle_tone():
    """Verify the rework is told the way out when changing the text alone cannot work.

    id: TST-QA-CONTRAST-005
    Given: A pale background carrying near-white text (unreadable) and near-black text (readable)
    When: The verdict is drawn
    Then: The defect names the other text colour on that background and asks for a background between the two tones,
          with the contrast to reach
    """
    samples = [_sample("L", [245, 245, 244], [254, 243, 199]), _sample("D", [12, 10, 9], [254, 243, 199])]
    defect = cc.verdict_from_samples("Desktop", samples).defects[0]
    assert "#0c0a09" in defect and "between the two" in defect and "3 to 1" in defect
    alone = cc.verdict_from_samples("Desktop", samples[:1]).defects[0]
    assert "between the two" not in alone and "3 to 1" in alone


def test_text_readable_elsewhere_keeps_its_colour_and_the_background_changes():
    """Verify the rework is not led to recolour a thing whose colour says what it is.

    id: TST-QA-CONTRAST-006
    Given: One text colour that reads well on a dark background and cannot be read on a pale one
    When: The verdict is drawn
    Then: The defect says where the colour reads well and asks to keep it and change the pale background; text
          unreadable on its only background gets no such advice
    """
    samples = [_sample("L", [245, 245, 244], [254, 243, 199]), _sample("L2", [245, 245, 244], [68, 64, 60])]
    defect = cc.verdict_from_samples("Desktop", samples).defects[0]
    assert "reads well on #44403c" in defect and "keep the text one colour" in defect
    assert "reads well" not in cc.verdict_from_samples("Desktop", samples[:1]).defects[0]


def test_the_defect_proposes_a_background_of_the_same_hue_that_both_texts_can_be_read_on():
    """Verify the rework is handed a colour that works, since a writer cannot measure one.

    id: TST-QA-CONTRAST-007
    Given: A pale yellow background carrying near-white text (unreadable) and near-black text
    When: The verdict is drawn
    Then: The defect proposes a background; it is darker than the pale one, still more red than blue as the pale one
          was, and both texts reach the asked contrast on it
    """
    light, dark, pale = [253, 252, 247], [28, 25, 23], [253, 230, 138]
    defect = cc.verdict_from_samples("Desktop", [_sample("L", light, pale), _sample("D", dark, pale)]).defects[0]
    proposed = defect.split("for example ")[1][:7]
    rgb = [int(proposed[i:i + 2], 16) for i in (1, 3, 5)]
    assert cc.contrast_ratio(light, rgb) >= 3 and cc.contrast_ratio(dark, rgb) >= 3
    assert rgb[0] > rgb[2] and sum(rgb) < sum(pale)
    crowded = cc.verdict_from_samples("Desktop", [_sample("a", [128, 128, 128], [130, 130, 130]),
                                                  _sample("b", [0, 0, 0], [130, 130, 130]),
                                                  _sample("c", [255, 255, 255], [130, 130, 130])]).defects[0]
    assert "No one tone carries all of that text" in crowded and "text now in #ffffff is drawn in #000000" in crowded


def test_when_no_tone_carries_all_the_text_the_defect_still_proposes_one_and_names_the_text_to_redraw():
    """Verify the rework is handed a way out also when a muted text stands between the light and the dark one.

    id: TST-QA-CONTRAST-008
    Given: A pale background carrying near-white text (unreadable), near-black text and a muted mid-grey text, so
           that no tone of the background lets all three be read
    When: The verdict is drawn
    Then: The defect proposes a background on which the near-white and the near-black text are read, and says the
          muted text is redrawn in the near-black colour there
    """
    light, dark, muted, pale = [245, 245, 244], [28, 25, 23], [87, 83, 78], [214, 211, 209]
    assert cc._between(pale, [light, dark, muted]) is None
    defect = cc.verdict_from_samples("Desktop", [_sample("L", light, pale), _sample("D", dark, pale),
                                                 _sample("M", muted, pale)]).defects[0]
    proposed = defect.split("for example ")[1][:7]
    rgb = [int(proposed[i:i + 2], 16) for i in (1, 3, 5)]
    assert cc.contrast_ratio(light, rgb) >= 3 and cc.contrast_ratio(dark, rgb) >= 3
    assert "text now in #57534e is drawn in #1c1917" in defect
