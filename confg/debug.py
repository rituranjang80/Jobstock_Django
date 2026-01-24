 def save(self, *args, **kwargs):
        # Print all FK fields and their values
        print("Saving:", self)
        for field in self._meta.fields:
            if isinstance(field, models.ForeignKey):
                rel_obj = getattr(self, field.name)
                print(f"ForeignKey {field.name}: {rel_obj} (id={getattr(rel_obj, 'id', None) if rel_obj else None})")
                if rel_obj and not rel_obj.pk:
                    print(f"WARNING: {field.name} is set but does not exist in DB!")
        super().save(*args, **kwargs)