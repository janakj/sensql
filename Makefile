modules := node-db presto proxy-db registry

.PHONY: build push
build push:
	@for m in $(modules); do            \
            $(MAKE) -C $$m $(MAKECMDGOALS); \
        done;

