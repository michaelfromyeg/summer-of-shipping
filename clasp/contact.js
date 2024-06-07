function contact() {
    const spreadsheetId = process.env.SPREADSHEET_ID;
    const sheetName = process.env.SHEET_NAME;

    const formLink = process.env.FORM_LINK;
    const zoomLink = process.env.ZOOM_LINK;

    const range = Sheets.Spreadsheets.Values.get(
        spreadsheetId,
        sheetName + "!A:G"
    );
    const data = range.values;

    let count = 0;

    for (let i = 1; i < data.length; i++) {
        const toEmail = data[i][1]; // Column B
        const name = data[i][2] || "there"; // Column C
        const contacted = data[i][6]; // Column G

        if (toEmail === "") {
            continue;
        }

        console.log(
            `Processing row ${i} with name=${name}, toEmail=${toEmail}, and contacted=${contacted}`
        );

        if (contacted.toString().toLowerCase() === "false") {
            const subject =
                "[Summer of Shipping] A welcome, a(nother) form, and the kick-off link!";
            const body = `Hey ${name}!\n\nWelcome to Summer of Shippping! I am truly overwhelmed by the response I've received so far (...300+ sign-ups in 24 hours!). I believe we can build (keyword: build) something special together this summer.\n\nI have a few more questions I'd love to ask beyond the initial intake survey, so please fill out this form at your earliest convenience: ${formLink}/.\n\nAs a reminder, our kick-off session will be this Thursday, at 5:00:00pm PST. Note that it'll be useful for both makers and mentors! Here's the link to the Zoom room: ${zoomLink}/. (Make sure you have a Zoom account; it's restricted so you'll need to sign-in.)\n\nI think that's all for now... see you Thursday!\n\nBest,\n\nMichael`;
            const htmlBody = `<p>Hey ${name}!</p><p>Welcome to Summer of Shipping! I am truly overwhelmed by the response I've received so far (...300+ sign-ups in 24 hours!). I believe we can build (keyword: build) something special together this summer.</p><p>I have a few more questions I'd love to ask beyond the initial intake survey, so please fill out <a href="${formLink}">this</a> form at your earliest convenience.</p><p>As a reminder, our kick-off session will be this Thursday, at 5:00:00pm PST. <a href="${zoomLink}">Here</a>'s the link to the Zoom room. (Make sure you have a Zoom account; it's restricted so you'll need to sign-in.)</p><p>(If that link doesn't work, copy and paste this into your browser: ${zoomLink})</p><p>I think that's all for now... see you Thursday!</p><p></p><p>Best,</p><p>Michael</p>`;

            console.log("Sending e-mail...");
            console.log({ to: toEmail, subject, body });

            GmailApp.sendEmail(toEmail, subject, body, { htmlBody });
            count = count + 1;

            // Update the "contacted" column (G) to TRUE
            Sheets.Spreadsheets.Values.update(
                {
                    values: [[true]],
                },
                spreadsheetId,
                sheetName + "!G" + (i + 1),
                {
                    valueInputOption: "RAW",
                }
            );
        }
    }

    console.log(`Done! Contacted ${count} makers.`);
}
