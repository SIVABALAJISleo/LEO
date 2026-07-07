import os
import glob
import re

def migrate_project(root_dir):
    # Search all .ts and .tsx files
    search_pattern = os.path.join(root_dir, 'src', '**', '*.ts*')
    files = glob.glob(search_pattern, recursive=True)
    
    count = 0
    for filepath in files:
        if not os.path.isfile(filepath):
            continue
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Check if file has supabase references
        if 'supabase' not in content.lower():
            continue
            
        # Pattern 1: import { supabase } from '@/integrations/supabase/client'
        # we alias it so the rest of the file still works: import { firebaseClient as supabase } from '@/integrations/firebase/client'
        new_content = re.sub(
            r"import\s*{\s*supabase\s*}\s*from\s*['\"]@/integrations/supabase/client['\"];?",
            "import { firebaseClient as supabase } from '@/integrations/firebase/client';",
            content
        )
        
        # Pattern 2: Any other imports from supabase module
        new_content = re.sub(
            r"from\s*['\"]@/integrations/supabase/client['\"]",
            "from '@/integrations/firebase/client'",
            new_content
        )
        
        # Pattern 3: Types imports
        new_content = re.sub(
            r"import\s*type\s*{\s*Database\s*}\s*from\s*['\"]@/integrations/supabase/types['\"];?",
            "// import type { Database } from '@/integrations/supabase/types';",
            new_content
        )

        if new_content != content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            count += 1
            print(f"Migrated: {filepath}")

    print(f"Migration complete. {count} files refactored to Firebase architectures.")

if __name__ == "__main__":
    # Use current directory
    migrate_project(".")
