def fix_openfix_pro():
    # Read the entire file
    with open('openfix_pro.py', 'r') as f:
        content = f.read()
    
    # Fix the error in the networkx visualization code
    old_code = """                except Exception as e:
            print(f"[INFO] Networkx save: {str(e)}")
    except Exception as e:
        print(f"[INFO] Visualization save operations: {str(e)}")"""
    
    new_code = """        except Exception as e:
            print(f"[INFO] Networkx save: {str(e)}")
    except Exception as e:
        print(f"[INFO] Visualization save operations: {str(e)}")"""
    
    # Replace the problematic code
    fixed_content = content.replace(old_code, new_code)
    
    # Write the fixed content back to the file
    with open('openfix_pro.py', 'w') as f:
        f.write(fixed_content)
    
    print("Fixed the syntax error in openfix_pro.py")

if __name__ == "__main__":
    fix_openfix_pro() 