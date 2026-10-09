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
