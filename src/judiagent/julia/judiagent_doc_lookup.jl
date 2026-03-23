#=
Julia Documentation Extractor for JUDIAgent

This script extracts function documentation from Julia source code,
specifically for functions defined in JUDI.jl. It uses CSTParser to
parse Julia code and extract function calls, then retrieves their
documentation using Julia's built-in documentation system.

Usage:
    julia julia_get_function_documentation.jl <path_or_file> [optional_file]

Arguments:
    path_or_file: Either a directory path or a Julia source file
    optional_file: If first arg is a directory, this specifies the main file

Output:
    Prints extracted function names and their documentation to stdout.
=#

using Base
using JUDI
using CSTParser
using CSTParser: EXPR


#=============================================================================
    Command Line Argument Processing
=============================================================================#

# Parse command line arguments to determine source file location
first_arg = abspath(ARGS[1])
path = isdir(first_arg) ? first_arg : dirname(first_arg)

# Determine the root file to analyze
root_file = if length(ARGS) > 1
    abspath(ARGS[2])
elseif isfile(first_arg)
    first_arg
else
    # Default to src/<dirname>.jl for package directories
    joinpath(path, "src", string(basename(path), ".jl"))
end

# Read the source code content
code_string = read(root_file, String)


#=============================================================================
    Documentation Retrieval
=============================================================================#

"""
    get_doc(funcname::String) -> String

Retrieve the documentation string for a given function name.

Searches through predefined modules (Main, JUDI) to find the function
and extract its documentation.

# Arguments
- `funcname::String`: Name of the function to look up

# Returns
- `String`: The documentation string, or empty string if not found

# Example
```julia
doc = get_doc("Model")
println(doc)  # Prints JUDI Model documentation
```
"""
function get_doc(funcname::String)
    # Modules to search for function definitions
    modules = [Main, JUDI]

    for mod in modules
        try
            if isdefined(mod, Symbol(funcname))
                # Retrieve documentation using Julia's @doc macro
                doc_expr = :(@doc $(Symbol(funcname)))
                doc = Core.eval(mod, doc_expr)

                if doc !== nothing
                    # Handle DocStr type (internal Julia documentation format)
                    if isa(doc, Base.Docs.DocStr)
                        doc_text = doc.text
                        if isa(doc_text, Core.SimpleVector) && length(doc_text) > 0
                            actual_doc = string(doc_text[1])
                            if !isempty(strip(actual_doc))
                                return actual_doc
                            end
                        elseif isa(doc_text, String)
                            return doc_text
                        end
                    else
                        # Fallback: convert to string representation
                        doc_str = string(doc)
                        if !isempty(strip(doc_str)) && doc_str != "nothing"
                            return doc_str
                        end
                    end
                end
            end
        catch e
            # Silently continue if documentation lookup fails
            continue
        end
    end
    return ""
end


#=============================================================================
    Function Name Extraction via CSTParser
=============================================================================#

"""
    extract_function_names(expr::EXPR) -> Vector{String}

Extract function names from a parsed Julia expression using CSTParser.

Traverses the AST to find function call nodes and extracts their names.

# Arguments
- `expr::EXPR`: Parsed Julia expression from CSTParser

# Returns
- `Vector{String}`: List of unique function names found in the expression
"""
function extract_function_names(expr::EXPR)
    function_names = Set{String}()

    function traverse(node)
        if isa(node, EXPR)
            # Check for function call nodes
            if haskey(node, :head) && node.head isa CSTParser.Head
                if node.head == CSTParser.CALL
                    # First child is the function name
                    if length(node.args) > 0
                        func_expr = node.args[1]
                        func_name = get_function_name(func_expr)
                        if func_name !== nothing && func_name != ""
                            push!(function_names, func_name)
                        end
                    end
                end
            end

            # Recursively traverse child nodes
            if haskey(node, :args) && node.args isa Vector
                for arg in node.args
                    traverse(arg)
                end
            end
        end
    end

    traverse(expr)
    return collect(function_names)
end


"""
    get_function_name(expr) -> Union{String, Nothing}

Extract the function name from a function expression node.

Handles various forms:
- Simple identifiers: `func_name`
- Parametric types: `func{T}`
- Qualified names: `Module.func`

# Arguments
- `expr`: Expression node from CSTParser

# Returns
- Function name as String, or nothing if not extractable
"""
function get_function_name(expr)
    if isa(expr, EXPR)
        if haskey(expr, :head) && haskey(expr, :val)
            if expr.head == CSTParser.IDENTIFIER
                return string(expr.val)
            elseif expr.head == CSTParser.CURLY
                # Parametric type: get base name
                if length(expr.args) > 0
                    return get_function_name(expr.args[1])
                end
            elseif expr.head == CSTParser.OP && string(expr.val) == "."
                # Qualified name: get last component
                if length(expr.args) >= 2
                    return get_function_name(expr.args[end])
                end
            end
        elseif haskey(expr, :val) && isa(expr.val, String)
            return expr.val
        end
    end
    return nothing
end


#=============================================================================
    Regex-Based Fallback Extraction
=============================================================================#

"""
    extract_function_names_regex(code_string::String) -> Vector{String}

Extract function names using regex pattern matching.

This is a more robust fallback that works when CSTParser has issues.
Identifies function calls by the pattern: identifier followed by `(`.

# Arguments
- `code_string::String`: Julia source code as a string

# Returns
- `Vector{String}`: List of unique function names found

# Note
Filters out Julia keywords that match the pattern but aren't functions.
"""
function extract_function_names_regex(code_string::String)
    function_names = Set{String}()

    # Pattern: word boundary, identifier, optional whitespace, opening paren
    pattern = Regex("\\b([a-zA-Z_][a-zA-Z0-9_]*)\\s*\\(")

    # Keywords to exclude from results
    keywords = Set(["if", "while", "for", "try", "catch", 
                    "function", "macro", "struct", "module"])

    for match in eachmatch(pattern, code_string)
        func_name = match.captures[1]
        if !in(func_name, keywords)
            push!(function_names, func_name)
        end
    end

    return collect(function_names)
end


"""
    parse_and_extract_functions(code_string::String) -> Vector{String}

Main entry point for function extraction.

Currently uses regex-based extraction as the primary method due to
its reliability across different Julia syntax variants.

# Arguments
- `code_string::String`: Julia source code to analyze

# Returns
- `Vector{String}`: List of function names found in the code
"""
function parse_and_extract_functions(code_string::String)
    return extract_function_names_regex(code_string)
end


#=============================================================================
    Text Processing Utilities
=============================================================================#

"""
    remove_leading_whitespace(text::String) -> String

Remove leading whitespace from each line of text.

Used to clean up documentation strings that may have excessive indentation.

# Arguments
- `text::String`: Multi-line text with potential leading whitespace

# Returns
- `String`: Text with leading whitespace removed from each line
"""
function remove_leading_whitespace(text::String)
    lines = split(text, '\n')
    processed_lines = String[]

    for line in lines
        trimmed_line = lstrip(line)
        push!(processed_lines, trimmed_line)
    end

    return join(processed_lines, '\n')
end


"""
    get_docs_for_functions(code_string::String) -> Tuple{String, Vector{String}}

Extract documentation for all functions found in the given code.

Main function that orchestrates the extraction and documentation retrieval process.

# Arguments
- `code_string::String`: Julia source code to analyze

# Returns
- `Tuple{String, Vector{String}}`: Documentation output string and list of 
  function names that had documentation

# Example
```julia
code = "using JUDI; model = Model(n, d, o, m)"
docs, funcs = get_docs_for_functions(code)
println(funcs)  # ["Model"]
println(docs)   # Model documentation
```
"""
function get_docs_for_functions(code_string::String)
    function_names = parse_and_extract_functions(code_string)
    println("Extracted function names: ", function_names)
    
    output = ""
    func_names_with_doc = String[]
    
    for func_name in function_names
        doc = string(get_doc(func_name))
        if !isempty(doc)
            push!(func_names_with_doc, func_name)
            
            # Format the documentation section
            output *= "\n# Documentation for '$func_name':\n"
            
            if isa(doc, String)
                # Convert markdown headers to avoid conflicts
                doc = replace(doc, r"^#"m => "##")
                # Clean up excessive indentation
                doc = remove_leading_whitespace(doc)
            end
            
            output *= doc * "\n"
        end
    end

    return output, func_names_with_doc
end


#=============================================================================
    Main Execution
=============================================================================#

# Run the documentation extraction and print results
documentation, func_names = get_docs_for_functions(code_string)

println("FUNCTION NAMES:")
println(func_names)
println("DOCUMENTATION")
println(documentation)
