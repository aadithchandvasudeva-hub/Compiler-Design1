#include <iostream>
#include <vector>
#include <string>
#include <cctype>
#include <stdexcept>

using namespace std;

// ---------- TOKEN ----------

enum TokenType {
    KEYWORD, IDENTIFIER, NUMBER,
    ASSIGN, PLUS, MINUS, MUL, DIV,
    LPAREN, RPAREN, SEMICOLON, END
};

struct Token {
    TokenType type;
    string value;
};

// ---------- LEXER ----------

class Lexer {
    string input;
    size_t pos = 0;

public:
    Lexer(const string& text) : input(text) {}

    vector<Token> tokenize() {
        vector<Token> tokens;

        while (pos < input.size()) {
            char c = input[pos];

            if (isspace(c)) { pos++; continue; }

            if (isalpha(c)) {
                string word;
                while (pos < input.size() &&
                       (isalnum(input[pos]) || input[pos]=='_'))
                    word += input[pos++];

                if (word=="int" || word=="float")
                    tokens.push_back({KEYWORD, word});
                else
                    tokens.push_back({IDENTIFIER, word});
                continue;
            }

            if (isdigit(c)) {
                string num;
                while (pos<input.size() && isdigit(input[pos]))
                    num += input[pos++];

                if (pos<input.size() && input[pos]=='.') {
                    num += input[pos++];
                    while (pos<input.size() && isdigit(input[pos]))
                        num += input[pos++];
                }

                tokens.push_back({NUMBER, num});
                continue;
            }

            switch(c) {
                case '=': tokens.push_back({ASSIGN,"="}); break;
                case '+': tokens.push_back({PLUS,"+"}); break;
                case '-': tokens.push_back({MINUS,"-"}); break;
                case '*': tokens.push_back({MUL,"*"}); break;
                case '/': tokens.push_back({DIV,"/"}); break;
                case '(': tokens.push_back({LPAREN,"("}); break;
                case ')': tokens.push_back({RPAREN,")"}); break;
                case ';': tokens.push_back({SEMICOLON,";"}); break;
                default:
                    throw runtime_error(string("Invalid character: ")+c);
            }
            pos++;
        }

        tokens.push_back({END,"EOF"});
        return tokens;
    }
};

// ---------- PARSER ----------

class Parser {
    vector<Token> tokens;
    size_t pos = 0;

    Token current() { return tokens[pos]; }
    void advance() { pos++; }

    void match(TokenType t) {
        if (current().type == t)
            advance();
        else
            throw runtime_error(
                "Syntax Error near token '" + current().value + "'");
    }

public:
    Parser(const vector<Token>& t) : tokens(t) {}

    void program() {
        cout << "\nParsing Program\n";
        while (current().type == KEYWORD)
            declaration();
        match(END);
        cout << "Program Syntax: VALID\n";
    }

    void declaration() {
        string type = current().value;
        match(KEYWORD);

        string name = current().value;
        match(IDENTIFIER);

        cout << "  Declaration: type=" << type
             << " name=" << name << "\n";

        if (current().type == ASSIGN) {
            match(ASSIGN);
            expression();
            cout << "    Assignment Expression OK\n";
        }

        match(SEMICOLON);
    }

    void expression() {
        term();
        while (current().type==PLUS || current().type==MINUS) {
            advance();
            term();
        }
    }

    void term() {
        factor();
        while (current().type==MUL || current().type==DIV) {
            advance();
            factor();
        }
    }

    void factor() {
        if (current().type==IDENTIFIER)
            match(IDENTIFIER);
        else if (current().type==NUMBER)
            match(NUMBER);
        else if (current().type==LPAREN) {
            match(LPAREN);
            expression();
            match(RPAREN);
        }
        else
            throw runtime_error(
                "Unexpected token '" + current().value + "'");
    }
};
//LOLA
// ---------- MAIN (USER INPUT) ----------

int main() {
    cout << "Enter Mini-C code (end with Ctrl+Z then Enter):\n\n";

    string line, code;
    while (getline(cin, line))
        code += line + "\n";

    try {
        Lexer lexer(code);
        auto tokens = lexer.tokenize();

        Parser parser(tokens);
        parser.program();
    }
    catch (exception& e) {
        cout << "\n" << e.what() << endl;
    }

    return 0;
}
