# Regex Search for Anki 2.1
This is an add-on for [Anki](https://apps.ankiweb.net/) version 2.1 that allows you to use regular expression pattern matching to search for cards in the **browser** and the **filtered deck creation dialog**. It also provides a feature that allows you to use wildcard pattern matching to specify a field name.

## Regex literal
You can use a regex literal as a search term, which consists of a regex pattern enclosed between **slashes**, as follows:

- `/ab+c/`
- `text:/Hello\b.*world/`

A regex search is case-**sensitive** by default. If you want to perform a regex search in a case-**insensitive** manner, add `i` flag to the end of a regex literal, as follows:

- `/ab+c/i`

## Wildcard matching on field names
#### Optional (Enabled by default)
As an optional feature, you can use wildcard pattern matching to specify a field name. A character `*` matches zero or more of any character. Field names are handled in a case-**insensitive** manner.

- `*text*:abc`
  - Find notes with a field whose name is **Text**, **text 1**, **English Text**, etc., and which contains a string **abc**. 

This feature can also be used in combination with regex search.

- `*info*:/hello\b.*world/i`

This feature can be disabled or the wildcard character can be changed via add-on's config dialog. 

- Go to *Tools* > *Add-ons* > Select this add-on > *Config*

## Note
[Anki's manual](https://apps.ankiweb.net/docs/manual.html#searching) says:

> If you want to search for something including a space or parenthesis, enclose it in quotes.

- `"/apple(?!\s*pie)/"`
- `"* foo *:abc"`

Keep this point in mind, since parentheses are often used in regular expression patterns.

## Known issues
This add-on conflicts with [Word search and wildcard field name (2.1)](https://ankiweb.net/shared/info/114749949) add-on.

## Installation
https://ankiweb.net/shared/info/2044559350
