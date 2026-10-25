# Things to ask

For ideas once your AI app is connected. Each example names the tools the AI will likely use.

## Find and read

- *Search for reviews of the Framework Laptop 13 from this year and give me the three most useful, with links.* (`search_many`, `read_many`)
- *Read this PDF and list the deadlines in it: https://example.com/guide.pdf* (`read_url`)
- *Research what changed in the latest Python release and cite your sources.* (`research`)

## Use the shared browser

- *Open the train company's site and find the cheapest ticket from Lyon to Paris next Friday morning. Don't buy anything.* (`browser_open`, `browser_look`, `browser_act`)
- *Log in to my energy account and download last month's bill.* The AI asks you to log in yourself with `browser_handoff`, then downloads the bill. (`browser_handoff`, `downloads_list`)
- *Check how my website looks on a phone.* (`browser_emulate`)

## Files

- *Read the invoice you just downloaded and tell me the total.* (`download_read`)
- *Attach the CV I dropped on the Files page to this job form, then stop before sending.* (`uploads_list`, `browser_upload`)

## Check pages

- *How fast is example.com on mobile, and what are the three biggest fixes?* (`pagespeed_check`)
- *Run the self test and tell me if anything fails.* (`self_test`)
