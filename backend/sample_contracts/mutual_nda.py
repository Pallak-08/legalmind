"""Generates a realistic mutual NDA as a DOCX file for evals and demos.

The text below is adapted from common open mutual-NDA templates. It is NOT
legal advice and should not be used for real agreements.
"""
from __future__ import annotations

from pathlib import Path

from docx import Document


NDA_TEXT = """MUTUAL NON-DISCLOSURE AGREEMENT

This Mutual Non-Disclosure Agreement (the "Agreement") is entered into as of June 14, 2026 (the "Effective Date") by and between Acme Robotics, Inc., a Delaware corporation ("Acme"), and Northwind Analytics LLC, a California limited liability company ("Northwind"). Acme and Northwind are each a "Party" and together the "Parties".

WHEREAS, the Parties wish to explore a potential business relationship (the "Purpose") and, in connection with such discussions, may disclose confidential information to one another; and

WHEREAS, the Parties wish to protect such confidential information on the terms set forth below;

NOW THEREFORE, in consideration of the mutual covenants herein, the Parties agree as follows:

1. DEFINITIONS

1.1 "Confidential Information" means any non-public information disclosed by one Party ("Discloser") to the other ("Recipient"), whether orally, in writing, or in any other form, that is marked as confidential or that a reasonable person would understand to be confidential given the nature of the information and the circumstances of disclosure. Confidential Information includes, without limitation, technical data, trade secrets, know-how, product plans, customer lists, financial information, and source code.

1.2 "Representatives" means a Party's directors, officers, employees, contractors, and professional advisors who have a need to know the Confidential Information for the Purpose and who are bound by written confidentiality obligations no less restrictive than those in this Agreement.

2. OBLIGATIONS OF RECIPIENT

2.1 The Recipient shall (a) use the Confidential Information solely for the Purpose; (b) protect the Confidential Information with at least the same degree of care it uses to protect its own confidential information of similar importance, but in no event less than reasonable care; and (c) not disclose the Confidential Information to any third party other than its Representatives without the Discloser's prior written consent.

2.2 The Recipient shall be responsible for any breach of this Agreement by its Representatives.

3. EXCLUSIONS

The obligations in Section 2 shall not apply to information that the Recipient can demonstrate: (a) was rightfully in the Recipient's possession without confidentiality obligation prior to disclosure by the Discloser; (b) is or becomes publicly available through no fault of the Recipient; (c) is rightfully received by the Recipient from a third party without a duty of confidentiality; or (d) is independently developed by the Recipient without use of or reference to the Discloser's Confidential Information.

4. COMPELLED DISCLOSURE

If the Recipient is required by law, subpoena, or court order to disclose Confidential Information, the Recipient shall, to the extent legally permitted, promptly notify the Discloser in writing so that the Discloser may seek a protective order or other appropriate remedy. The Recipient shall disclose only the portion of Confidential Information that is legally required and shall use reasonable efforts to obtain confidential treatment of any disclosed information.

5. TERM AND TERMINATION

5.1 This Agreement shall commence on the Effective Date and shall continue for a period of two (2) years thereafter, unless earlier terminated in accordance with this Section 5.

5.2 Either Party may terminate this Agreement for any reason upon thirty (30) days prior written notice to the other Party.

5.3 The Recipient's confidentiality obligations under Section 2 shall survive termination of this Agreement for a period of three (3) years from the date of disclosure of the relevant Confidential Information; provided, however, that with respect to information that constitutes a trade secret under applicable law, such obligations shall continue for so long as such information remains a trade secret.

6. RETURN OR DESTRUCTION OF MATERIALS

Upon written request by the Discloser or upon termination of this Agreement, the Recipient shall promptly return or destroy all Confidential Information of the Discloser in its possession or control, including all copies and derivatives, and shall certify such return or destruction in writing if requested. Notwithstanding the foregoing, the Recipient may retain one (1) archival copy solely for legal compliance purposes, subject to the confidentiality obligations of this Agreement.

7. NO LICENSE; NO WARRANTY

7.1 No license or right to any intellectual property is granted by this Agreement, by implication, estoppel, or otherwise, except the limited right to use the Confidential Information for the Purpose.

7.2 ALL CONFIDENTIAL INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND. NEITHER PARTY MAKES ANY REPRESENTATION OR WARRANTY AS TO THE ACCURACY OR COMPLETENESS OF ANY CONFIDENTIAL INFORMATION.

8. REMEDIES

The Parties acknowledge that monetary damages may be inadequate to remedy a breach of this Agreement and that the non-breaching Party shall be entitled to seek injunctive relief in addition to any other remedies available at law or in equity, without the necessity of posting a bond.

9. GENERAL PROVISIONS

9.1 Governing Law. This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware, without regard to its conflict of laws principles.

9.2 Dispute Resolution. Any dispute arising under this Agreement shall be resolved by binding arbitration administered by JAMS in San Francisco, California, in accordance with its Comprehensive Arbitration Rules and Procedures.

9.3 Entire Agreement. This Agreement constitutes the entire agreement between the Parties regarding its subject matter and supersedes all prior agreements and understandings, whether written or oral.

9.4 Assignment. Neither Party may assign this Agreement without the prior written consent of the other Party, except in connection with a merger, acquisition, or sale of substantially all of its assets.

9.5 Notices. All notices under this Agreement shall be in writing and delivered to the addresses set forth above, or to such other address as a Party may designate in writing. Notice shall be deemed given upon receipt.

9.6 Severability. If any provision of this Agreement is held to be invalid or unenforceable, the remaining provisions shall continue in full force and effect.

IN WITNESS WHEREOF, the Parties have executed this Agreement as of the Effective Date.
"""


def generate_nda_docx(output_path: str | Path) -> Path:
    output_path = Path(output_path)
    doc = Document()
    for paragraph in NDA_TEXT.split("\n\n"):
        doc.add_paragraph(paragraph.strip())
    output_path.parent.mkdir(parents=True, exist_ok=True)
    doc.save(output_path)
    return output_path


if __name__ == "__main__":
    out = generate_nda_docx(Path(__file__).parent / "sample_mutual_nda.docx")
    print(f"Wrote {out}")
